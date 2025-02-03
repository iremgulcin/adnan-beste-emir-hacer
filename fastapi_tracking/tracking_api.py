import os
import cv2
import yt_dlp
import asyncio  # asyncio modülünü ekliyoruz
from ultralytics import YOLO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

app = FastAPI()

# Sınıf isimleri
class_names = [
    "echinus_esculentus", "gambusia_holbrooki", "lagocephalus_sceleratus",
    "lepomis-gibbosus", "pseudorasbora-parva", "pterois_miles",
    "sargocentron_rubrum", "siganus-rivulatus"
]

@app.get("/")
def read_root():
    return {"message": "Tracking API is running!"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    video_file_path = "input_video.mp4"
    model_path = "/home/hacer/yolo_tracking_backend/deneme_best.pt"

    try:
        # İlk gelen mesaj: YouTube URL'sini al
        youtube_url = await websocket.receive_text()

        # YouTube videosunu indir
        ydl_opts = {'format': 'best', 'outtmpl': video_file_path}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # YOLO modelini yükle
        model = YOLO(model_path)

        # Videoyu aç
        cap = cv2.VideoCapture(video_file_path)
        if not cap.isOpened():
            await websocket.send_text("Video açma başarısız.")
            await websocket.close()
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Nesne tespiti
            results = model(frame, stream=True)

            for result in results:
                if hasattr(result, "boxes"):
                    for box in result.boxes.data.tolist():
                        x1, y1, x2, y2, conf, cls = box
                        class_name = class_names[int(cls)] if int(cls) < len(class_names) else "unknown"

                        # Bounding box çiz
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                        # Etiket yaz
                        label = f"{class_name} ({conf:.2f})"
                        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Çerçeveyi JPEG formatına dönüştür ve WebSocket ile gönder
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())
            
            # Video hızını ayarlamak için bir süre bekle (frame rate)
            await asyncio.sleep(1 / 10)  # 30 fps için bekleme

    except yt_dlp.utils.DownloadError as e:
        await websocket.send_text(f"Video indirme başarısız: {str(e)}")
    except WebSocketDisconnect:
        print("WebSocket bağlantısı kesildi.")
    except Exception as e:
        await websocket.send_text(f"Hata oluştu: {str(e)}")
    finally:
        # Kaynakları serbest bırak
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
        await websocket.close()
        if 'cap' in locals():
            cap.release()
