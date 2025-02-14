import os
import cv2
import json
import yt_dlp
import asyncio
from ultralytics import YOLO
import numpy as np
from yolox.tracker.byte_tracker import BYTETracker
import argparse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

app.mount("/videos", StaticFiles(directory="videos"), name="videos")

parser = argparse.ArgumentParser()
parser.add_argument('--track_thresh', type=float, default=0.6, help='Tracking confidence threshold')
parser.add_argument('--mot20', action='store_true', help='Use MOT20 dataset format')
parser.add_argument('--save_results', action='store_true', help='Save tracking results')
parser.add_argument('--vis', action='store_true', help='Visualize tracking')
parser.add_argument('--show', action='store_true', help='Show tracking output on the screen')
parser.add_argument('--device', default='cpu', help='Device for inference (cpu or cuda)')
parser.add_argument('--track_buffer', type=int, default=100, help='Number of frames to keep lost targets in buffer')
args = parser.parse_args([]) 

# Detection API
@app.websocket("/detection_ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    video_file_path = "input_video.mp4"
    output_video_path = "/home/hacer/Desktop/flutter_deneme_01/assets/videos/output_video.mp4"  # Sonucun kaydedileceği dosya
    model_path = "/home/hacer/yolo_tracking_backend/best.pt"  

    try:
        # İlk gelen mesaj JSON olarak çözülmeli
        message = await websocket.receive_text()
        data = json.loads(message)  # JSON string'i dict formatına çevir
        youtube_url = data.get("video_url")  

        if not youtube_url:
            await websocket.send_text("Geçerli bir YouTube URL'si gönderin.")
            await websocket.close()
            return

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

        # Video özelliklerini al
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # VideoWriter ayarla (MP4 formatında kaydetmek için)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

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
                        class_names = model.names
                        class_name = class_names[int(cls)] if int(cls) < len(class_names) else "unknown" 
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                        label = f"{class_name} ({conf:.2f})"
                        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            out.write(frame)           
            
            # Çerçeveyi JPEG formatına dönüştür ve WebSocket ile gönder
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())

            # Video hızını ayarlamak için bir süre bekle (frame rate)
            await asyncio.sleep(1 / 10) 

    except json.JSONDecodeError:
        await websocket.send_text("JSON formatı hatalı.")
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
        if os.path.exists(output_video_path):
            await websocket.send_text(f"İşlenmiş video kaydedildi: {output_video_path}")
        await websocket.close()
        if 'cap' in locals():
            cap.release()
        if 'out' in locals():
            out.release() 


# ByteTrack API
@app.websocket("/byte_track_ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    video_file_path = "input_video.mp4"
    output_video_path = "videos/output_video_track.mp4"  # Sonucun kaydedileceği dosya
    model_path = "/home/hacer/yolo_tracking_backend/best.pt"
    tracker = BYTETracker(args)
    
    try:
        # İlk gelen mesaj JSON olarak çözülmeli
        message = await websocket.receive_text()
        data = json.loads(message)  # JSON string'i dict formatına çevir
        youtube_url = data.get("video_url") 

        if not youtube_url:
            await websocket.send_text("Geçerli bir YouTube URL'si gönderin.")
            await websocket.close()
            return

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

        # Video özelliklerini al
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # VideoWriter ayarla (MP4 formatında kaydetmek için)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame) 
            detections = []  
            classes = []  
            confidences = []  
            
            for result in results:
                boxes = result.boxes.xyxy  # Bounding box'ları al (xyxy formatında)
                confidences = result.boxes.conf  
                cls = result.boxes.cls  

                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box
                    confidence = confidences[i].item()  
                    class_id = int(cls[i].item())  

                    if confidence > 0.4:  # Sadece güven seviyesi > 0.4 olanları ekle (optimize edilmiş)
                        detections.append([int(x1), int(y1), int(x2), int(y2), confidence])
                        classes.append(class_id)

            detections = np.array(detections)  
            img_info = np.array([frame.shape[1], frame.shape[0], 1.0])  
            img_size = np.array([frame.shape[1], frame.shape[0]]) 

            if detections.shape[0] > 0:
                tracked_objects = tracker.update(detections, img_info, img_size)
            else:
                tracked_objects = []  

            for obj in tracked_objects:
                box = obj.tlwh  
                track_id = obj.track_id  
                x1, y1, width, height = box  

                x1, y1, x2, y2 = map(int, [x1, y1, x1 + width, y1 + height])

                label = model.names[classes[tracked_objects.index(obj)]] if classes else 'Unknown'

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                out.write(frame)
            # Çerçeveyi JPEG formatına dönüştür ve WebSocket ile gönder
            _, buffer = cv2.imencode(".jpg", frame)
            await websocket.send_bytes(buffer.tobytes())

            # Video hızını ayarlamak için bir süre bekle (frame rate)
            await asyncio.sleep(1 / 10)  

    except json.JSONDecodeError:
        await websocket.send_text("JSON formatı hatalı.")
    except yt_dlp.utils.DownloadError as e:
        await websocket.send_text(f"Video indirme başarısız: {str(e)}")
    except WebSocketDisconnect:
        print("WebSocket bağlantısı kesildi.")
    except Exception as e:
        await websocket.send_text(f"Hata oluştu: {str(e)}")
    finally:
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
        if os.path.exists(output_video_path):
            await websocket.send_text(f"İşlenmiş video kaydedildi: {output_video_path}")
        await websocket.close()
        if 'cap' in locals():
            cap.release()
        if 'out' in locals():
            out.release()  


@app.get("/")
def root():
    return {"message": "API Çalışıyor!"}
