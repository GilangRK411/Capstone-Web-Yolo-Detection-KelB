# mqtt_client.py
import paho.mqtt.client as mqtt
from config import *
# Import library MQTT dan konfigurasi

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
# Inisialisasi client MQTT dan set username/password

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke MQTT Broker")
    else:
        print(f"Gagal terhubung ke MQTT dengan kode: {rc}")
# Callback saat koneksi ke broker berhasil/gagal

def on_publish(client, userdata, mid):
    print(f"Pesan terkirim dengan ID: {mid}")
# Callback saat pesan berhasil dikirim

mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
# Set callback ke client MQTT

def connect_mqtt():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client.loop_start()  # Memulai loop MQTT di background
    except Exception as e:
        print("Gagal terhubung ke MQTT:", e)
# Fungsi untuk koneksi ke broker MQTT dan mulai loop
