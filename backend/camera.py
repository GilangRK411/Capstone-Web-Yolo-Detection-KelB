# camera.py
import cv2
import numpy as np
import torch
import time
import threading
from queue import Queue
from ultralytics import YOLO
from config import *
from mqtt_client import mqtt_client
import paho.mqtt.client as mqtt
# Import library yang dibutuhkan untuk kamera, deteksi, dan MQTT

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"[INFO] Menggunakan device: {device}")
# Pilih device GPU jika ada, jika tidak pakai CPU

model = YOLO("yolo11n.pt").to(device)
frame_queue = Queue(maxsize=2)
capture_event = threading.Event()
last_mqtt_send_time = time.time()
last_detection = None
last_detection_time = time.time()
detection_buffer = []  # Buffer status deteksi
DETECTION_BUFFER_SIZE = 5  # Jumlah frame konfirmasi
DETECTION_DELAY = 2.0  # Delay sebelum kirim status baru
# Inisialisasi model YOLO, queue frame, dan event kontrol

def create_dummy_image():
    return np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
# Membuat gambar kosong (dummy)

def get_video_capture():
    print(f"[INFO] Mencoba terhubung ke kamera: {RTSP_URL}")
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
    time.sleep(1)
    if not cap.isOpened():
        print("Gagal terhubung ke kamera RTSP, mencoba kamera default...")
        cap.release()
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Tidak ada kamera yang tersedia.")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    print("Berhasil terhubung ke kamera")
    return cap
# Fungsi untuk koneksi ke kamera RTSP atau webcam

def draw_detections(frame, detections):
    if detections is None:
        return frame
    annotated = frame.copy()
    for result in detections:
        for box in result.boxes:
            label = result.names[int(box.cls[0].item())]
            if label == "person":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated, f'{label} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return annotated
# Gambar kotak dan label pada frame jika terdeteksi orang

def should_send_detection(current_status):
    global detection_buffer, last_detection_time
    detection_buffer.append(current_status)
    if len(detection_buffer) > DETECTION_BUFFER_SIZE:
        detection_buffer.pop(0)
    person_count = detection_buffer.count(True)
    detection_percentage = (person_count / len(detection_buffer)) * 100
    current_time = time.time()
    time_since_last_detection = current_time - last_detection_time
    if time_since_last_detection >= DETECTION_DELAY:
        if (current_status and detection_percentage >= 60) or \
           (not current_status and detection_percentage <= 40):
            last_detection_time = current_time
            return True
    return False
# Logika agar status deteksi tidak terlalu sering dikirim

def capture_frames():
    global last_mqtt_send_time, last_detection, last_detection_time
    cap = get_video_capture()
    if cap is None:
        return
    _ = model.predict(source=create_dummy_image(), device=device)
    frame_count = 0
    retry_count = 0
    max_retries = 3
    last_frame_time = time.time()
    current_detection_status = False
    while capture_event.is_set():
        try:
            current_time = time.time()
            if current_time - last_frame_time < 1/30:
                time.sleep(0.001)
                continue
            success, frame = cap.read()
            if not success:
                retry_count += 1
                print(f"Gagal membaca frame (percobaan {retry_count}/{max_retries})")
                if retry_count >= max_retries:
                    print("Mencoba reconnect ke kamera...")
                    cap.release()
                    cap = get_video_capture()
                    if cap is None:
                        break
                    retry_count = 0
                time.sleep(0.5)
                continue
            retry_count = 0
            frame_count += 1
            detected_person = False
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            if frame_count % PREDICT_EVERY_N_FRAMES == 0:
                try:
                    results = model.predict(frame, device=device, verbose=False)
                    last_detection = results
                    for result in results:
                        for box in result.boxes:
                            label = result.names[int(box.cls[0].item())]
                            if label == "person":
                                detected_person = True
                    current_detection_status = detected_person
                except Exception as e:
                    print(f"Error dalam prediksi: {e}")
            annotated = draw_detections(frame, last_detection)
            now = time.time()
            if now - last_mqtt_send_time >= MQTT_SEND_INTERVAL:
                if should_send_detection(current_detection_status):
                    message = "person_detected" if current_detection_status else "no_person_detected"
                    try:
                        result = mqtt_client.publish(MQTT_TOPIC, message, qos=1)
                        result.wait_for_publish()
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            print(f"MQTT terkirim: {message}")
                    except Exception as e:
                        print(f"Gagal kirim MQTT: {e}")
                    last_mqtt_send_time = now
            if not frame_queue.full():
                frame_queue.put_nowait(annotated)
            last_frame_time = current_time
        except Exception as e:
            print(f"Error dalam capture_frames: {e}")
            time.sleep(0.5)
    cap.release()
# Fungsi utama untuk ambil frame, deteksi, dan kirim status ke MQTT

def generate_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get_nowait()
            try:
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as e:
                print(f"Error dalam generate_frames: {e}")
        time.sleep(1/30)
# Generator untuk streaming frame hasil deteksi ke web
