# app.py
from flask import Flask, Response, render_template
from flask_cors import CORS
from camera import capture_event, capture_frames, generate_frames
from mqtt_client import connect_mqtt
import threading
import torch
# Import library dan modul yang dibutuhkan

app = Flask(__name__)
CORS(app)
# Inisialisasi Flask dan aktifkan CORS

@app.route('/')
def index():
    return render_template('index.html')
# Endpoint utama, tampilkan halaman index

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# Endpoint untuk streaming video hasil deteksi

@app.route('/camera_on')
def camera_on():
    global t
    if not capture_event.is_set():
        capture_event.set()
        t = threading.Thread(target=capture_frames)
        t.daemon = True
        t.start()
        return "Kamera dihidupkan", 200
    else:
        return "Kamera sudah aktif", 200
# Endpoint untuk menyalakan kamera (mulai deteksi)

@app.route('/camera_off')
def camera_off():
    if capture_event.is_set():
        capture_event.clear()
        return "Kamera dimatikan", 200
    else:
        return "Kamera sudah nonaktif", 200
# Endpoint untuk mematikan kamera (stop deteksi)

if __name__ == '__main__':
    connect_mqtt()
    torch.cuda.empty_cache()
    app.run(debug=False, host='0.0.0.0', port=5000)
# Jalankan server Flask dan koneksi MQTT
