# config.py
MQTT_BROKER = "##.#.##.##"
MQTT_PORT = 0000
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "yolo/detection_status"
# Konfigurasi untuk koneksi MQTT

# Format RTSP untuk Hikvision
RTSP_URL = "rtsp://#####:##########@##.#.###.###:###/Streaming/Channels/102"
# Alamat stream kamera RTSP

# Menurunkan resolusi untuk performa lebih baik
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
PREDICT_EVERY_N_FRAMES = 3
MQTT_SEND_INTERVAL = 5
# Pengaturan resolusi, interval deteksi, dan interval kirim MQTT
