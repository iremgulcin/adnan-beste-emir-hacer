import cv2
import os

def extract_frames(video_path, output_folder, frame_rate=1):

    # Çıktı klasörü yoksa oluştur
    os.makedirs(output_folder, exist_ok=True)
    
    # Videoyu aç
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Video açılamadı: {video_path}")
        return
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Frame numarasına göre kaydet
        if frame_count % frame_rate == 0:
            output_file = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(output_file, frame)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"{saved_count} frame kaydedildi. Çıktı klasörü: {output_folder}")


# Kullanım örneği
video_path = "/home/hacer/Desktop/istilacı balık türleri/data_retrieval/balon-balığı/7.mp4"  
output_folder = "/home/hacer/Desktop/istilacı balık türleri/data_retrieval/balon-balığı/7"  
frame_rate = 20  

extract_frames(video_path, output_folder, frame_rate)
