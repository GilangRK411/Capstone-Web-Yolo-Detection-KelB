#!/bin/bash

echo " ^=^z^` Memulai setup untuk YOLO Backend + MQTT..."

# Update dan install basic tools
apt update && apt install -y \
    python3-venv \
    python3-pip \
    git \
    coreutils \
    mosquitto \
    mosquitto-clients \
    libgl1 \
    libglib2.0-0

# Masuk ke direktori backend
cd ~/Capstone-Web-Yolo-Detection/backand || {
    echo " ^}^l Folder backand tidak ditemukan"
    exit 1
}

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependensi Python
pip install --upgrade pip
pip install ultralytics flask flask-cors opencv-python paho-mqtt

echo " ^|^e Semua dependensi terinstall."

# Jalankan aplikasi (opsional, bisa dikomentari jika hanya ingin setup)
echo " ^=^z^` Menjalankan backend Flask..."
python app.py
