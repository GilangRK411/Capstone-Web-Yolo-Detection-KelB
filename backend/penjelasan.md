# Penjelasan Kode Backend

Dokumen ini memberikan penjelasan singkat mengenai setiap file Python yang ada di dalam direktori backend.

## `app.py`

File ini adalah titik masuk utama untuk aplikasi backend. `app.py` menggunakan framework Flask untuk membuat sebuah web server sederhana. Server ini memiliki beberapa endpoint: untuk menyajikan halaman web utama, untuk memulai dan menghentikan proses pengambilan gambar dari kamera, serta untuk menyediakan _stream_ video yang sudah diproses. Selain itu, file ini juga bertanggung jawab untuk memulai koneksi ke broker MQTT saat aplikasi dijalankan.

## `camera.py`

File `camera.py` berisi semua logika yang terkait dengan operasi kamera dan deteksi objek. File ini berfungsi untuk terhubung ke sumber video (baik itu stream RTSP atau kamera lokal), mengambil frame video secara terus-menerus, dan melakukan deteksi objek menggunakan model YOLO untuk mengidentifikasi keberadaan manusia (_person_). Setiap frame yang diproses akan ditambahkan anotasi berupa kotak pembatas (bounding box) jika manusia terdeteksi. File ini juga mengelola sebuah antrian (queue) untuk frame yang akan ditampilkan di _stream_ video dan mengatur pengiriman status deteksi (misalnya "person_detected" atau "no_person_detected") ke topik MQTT secara berkala dan efisien menggunakan sistem _buffering_.

## `config.py`

File ini berfungsi sebagai pusat konfigurasi untuk seluruh aplikasi backend. `config.py` menyimpan semua variabel dan parameter penting dalam bentuk konstanta. Ini mencakup informasi kredensial dan alamat untuk koneksi ke broker MQTT, URL untuk stream RTSP kamera, pengaturan resolusi video, serta interval untuk frekuensi deteksi objek dan pengiriman pesan MQTT. Memisahkan konfigurasi ke dalam file ini memungkinkan perubahan pengaturan dengan mudah tanpa harus memodifikasi kode logika utama.

## `mqtt_client.py`

File `mqtt_client.py` bertanggung jawab untuk menangani semua interaksi dengan broker MQTT. File ini menggunakan library `paho-mqtt` untuk membuat dan mengkonfigurasi instance client MQTT. Di dalamnya, terdapat fungsi untuk terhubung ke broker, serta fungsi _callback_ yang akan dieksekusi ketika koneksi berhasil atau ketika sebuah pesan berhasil dipublikasikan. Logika koneksi dijalankan di _background thread_, sehingga tidak menghalangi proses utama aplikasi.

# Panduan Setup Backend YOLO + MQTT

File `setup.sh` ini digunakan untuk mempersiapkan lingkungan backend YOLO dan MQTT secara otomatis. Berikut adalah penjelasan langkah-langkah yang dilakukan oleh script ini:

## Langkah-langkah Setup

1. **Update & Install Tools Dasar**
   - Script akan memperbarui daftar paket dan menginstal beberapa tools penting seperti Python, pip, git, coreutils, Mosquitto (MQTT broker & client), serta library pendukung OpenCV (`libgl1`, `libglib2.0-0`).

2. **Masuk ke Direktori Backend**
   - Script akan berpindah ke folder `backand` di dalam project. Jika folder tidak ditemukan, proses akan berhenti.

3. **Membuat Virtual Environment**
   - Script akan membuat virtual environment Python bernama `venv` dan mengaktifkannya. Ini bertujuan agar dependensi Python terisolasi dari sistem utama.

4. **Install Dependensi Python**
   - Script akan meng-upgrade pip dan menginstal semua library Python yang dibutuhkan, yaitu:
     - `ultralytics` (YOLO)
     - `flask` (web server)
     - `flask-cors` (CORS support)
     - `opencv-python` (pengolahan gambar)
     - `paho-mqtt` (client MQTT)

5. **Menjalankan Backend Flask**
   - Setelah semua dependensi terpasang, script akan menjalankan aplikasi backend (`app.py`).
   - Bagian ini opsional, bisa dikomentari jika hanya ingin melakukan setup tanpa menjalankan server.

## Cara Menggunakan

1. Pastikan Anda sudah berada di dalam folder project utama.
2. Jalankan script dengan perintah:
   ```bash
   bash backand/setup.sh
   ```
3. Ikuti instruksi yang muncul di terminal.

---

Jika terjadi error, pastikan semua dependensi sistem sudah terpasang dan Anda memiliki akses root/sudo untuk instalasi paket. 