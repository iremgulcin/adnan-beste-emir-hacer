from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import shutil
import os
from dotenv import load_dotenv
from database import SessionLocal, Video, AnimalInfo
from sqlalchemy.orm import Session
from datetime import datetime
from database import Detection

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')
load_dotenv()

app = FastAPI()

# CORS Middleware ekleyelim
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modeli yükle
MODEL_PATH = os.getenv("MODEL_PATH", "models/best.pt")
model = YOLO(MODEL_PATH)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "backend/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file.filename
    unique_filename = f"{timestamp}_{original_filename}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save to database with unique filename
    db_video = Video(filename=unique_filename)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)

    return {"message": "Video yüklendi", "file_name": unique_filename, "video_id": db_video.id}


@app.get("/process/{video_id}")
def process_video(video_id: int, db: Session = Depends(get_db)):
    # Videoyu veritabanından al
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Video dosyasının tam yolunu oluştur
    full_video_path = os.path.join(UPLOAD_DIR, db_video.filename)
    if not os.path.exists(full_video_path):
        raise HTTPException(status_code=404, detail=f"Video file not found: {full_video_path}")

    # Durumu "işleniyor" olarak güncelle
    db_video.status = "processing"
    db.commit()

    # Videoyu işle
    cap = cv2.VideoCapture(full_video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # İşlenmiş dosya adı ve çıktı yolu
    processed_filename = f"processed_{db_video.filename}"
    output_path = os.path.join(UPLOAD_DIR, processed_filename)

    # macOS için 'avc1' codec kullan
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        20.0,
        (frame_width, frame_height)
    )

    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        results = model(frame)  # Model ile tespit yap
        for r in results:
            for box, cls_id, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                x1, y1, x2, y2 = map(int, box[:4])

                # Detection çerçevesini çiz (açık mavi renk: #80e3ff -> BGR(255, 227, 128))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 227, 128), 2)

                # Hayvan adı ve güven skorunu al
                class_name = model.names[int(cls_id)]
                confidence = float(conf)

                # Hayvan adı ve güven skorunu ekrana yazdır
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),  # Metnin konumu
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,  # Font ölçeği
                    (255, 255, 255),  # Metin rengi (beyaz)
                    2  # Kalınlık
                )

                # Tespiti veritabanına kaydet
                detection = Detection(
                    video_id=video_id,
                    animal_type=class_name,
                    confidence=confidence,
                    frame_number=frame_number
                )
                db.add(detection)

        out.write(frame)  # İşlenmiş kareyi çıktıya yaz

    cap.release()
    out.release()

    # Tüm tespitleri veritabanına kaydet
    db.commit()

    # İşlenmiş dosya bilgilerini veritabanına kaydet
    db_video.processed_filename = processed_filename
    db_video.status = "completed"
    db.commit()

    # İşlenmiş videonun URL'sini oluştur
    video_url = f"http://0.0.0.0:8000/video/{video_id}"
    return {
        "message": "İşleme tamamlandı",
        "video_id": video_id,
        "video_url": video_url
    }


@app.get("/video/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    if db_video.processed_filename:
        video_path = os.path.join(UPLOAD_DIR, db_video.processed_filename)
    else:
        video_path = os.path.join(UPLOAD_DIR, db_video.filename)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(video_path, media_type="video/mp4")

# Add new endpoint to get detections for a video
@app.get("/detections/{video_id}")
def get_detections(video_id: int, db: Session = Depends(get_db)):
    detections = db.query(Detection).filter(Detection.video_id == video_id).all()
    return {
        "video_id": video_id,
        "detections": [
            {
                "animal_type": d.animal_type,
                "confidence": d.confidence,
                "frame_number": d.frame_number,
                "timestamp": d.timestamp
            }
            for d in detections
        ]
    }

@app.get("/model-classes")
def get_model_classes():
    return {"classes": model.names}

@app.get("/animal-info/{species_name}")
def get_animal_info(species_name: str, db: Session = Depends(get_db)):

    animal_info = db.query(AnimalInfo).filter(AnimalInfo.species_name == species_name).first()
    if not animal_info:
        raise HTTPException(status_code=404, detail="Animal information not found")
    return animal_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)