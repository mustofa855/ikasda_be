# Ikasda Backend

Ini adalah backend untuk situs **Ikasda (Ikatan Alumni)** yang dibangun menggunakan Django. Proyek ini menyediakan berbagai fitur seperti manajemen berita dan event, direktori alumni, galeri, serta sistem feedback dan diskusi.

## Fitur Utama

- **Manajemen Berita dan Event:**  
  Buat, edit, dan tampilkan berita serta event yang berkaitan dengan kegiatan alumni, seperti donor darah, reuni, dan lain-lain.
- **Direktori Alumni:**  
  Data alumni dengan fitur pencarian yang memungkinkan pengguna untuk menemukan alumni berdasarkan nama atau angkatan.
- **Galeri Foto:**  
  Unggah dan tampilkan gambar dalam galeri dan album, dengan nama file diubah secara acak untuk menjaga keamanan.
- **Feedback dan Diskusi:**  
  Sistem untuk memberikan kesan & pesan serta berdiskusi di antara pengguna.
- **Autentikasi dengan JWT:**  
  Menggunakan Django REST Framework dan Simple JWT untuk mengamankan API.

## Teknologi yang Digunakan

- **Django** – Framework web untuk backend.
- **MySQL** – Database untuk penyimpanan data.
- **Django REST Framework** – Untuk pembuatan API.
- **Simple JWT** – Untuk autentikasi menggunakan JSON Web Token.
- **WhiteNoise** – Untuk penyajian static files pada production.

## Struktur Proyek

Struktur direktori proyek Anda diharapkan seperti berikut:

ikasda_bev1/ 
├── manage.py 
├── project/ # Folder berisi pengaturan Django, urls, wsgi, dsb. 
├── app/ # Folder aplikasi (jika ada) 
├── core/ # Aplikasi inti dengan models, views, serializers, dll. 
├── media/ # Tempat penyimpanan file upload (tidak termasuk ke repository) 
└── .gitignore # File ignore untuk Git


## Instalasi dan Setup

1. **Clone Repository**

   Clone repository ke mesin lokal Anda:
   ```bash
   git clone https://github.com/username/ikasda_bev1.git
   cd ikasda_bev1

2. **Buat Virtual Environment dan Install Dependencies**
python -m venv env
# Untuk Windows:
env\Scripts\activate
# Untuk macOS/Linux:
source env/bin/activate

3. **Install semua dependensi (pastikan file requirements.txt sudah ada):**

bash
Salin
Edit
pip install -r requirements.txt

**4.Konfigurasi Database**

Perbarui file settings.py dengan konfigurasi database Anda. Proyek ini menggunakan MySQL. Pastikan Anda telah menginstal MySQL dan mengonfigurasi koneksi dengan benar.

**5.Jalankan Migrasi**

Buat dan jalankan migrasi untuk menerapkan perubahan struktur database:

python manage.py makemigrations
python manage.py migrate

**6.Buat Superuser**

Buat akun admin untuk mengakses panel admin Django:

python manage.py createsuperuser

**7.Jalankan Server Pengembangan**

Mulai server development:

python manage.py runserver
Akses situs pada http://127.0.0.1:8000.

Pengaturan File Sensitif
.env File:
Untuk variabel rahasia seperti SECRET_KEY, gunakan file .env dan package seperti django-environ agar nilai tersebut tidak langsung tersimpan di kode. Pastikan file .env sudah ditambahkan ke file .gitignore.

.gitignore:
Pastikan file .gitignore mencakup file dan folder seperti virtual environment, file database (jika menggunakan SQLite), folder media, dan file konfigurasi rahasia.

Contoh .gitignore:
# Bytecode Python
*.pyc
__pycache__/

# Virtual environment
env/
venv/

# Database
db.sqlite3

# File media yang diupload
media/

# File konfigurasi rahasia
.env

# Log file
*.log


**Kontribusi**
Kontribusi sangat disambut! Silakan fork repository ini, buat branch untuk fitur baru atau perbaikan bug, lalu buat pull request untuk review. Pastikan commit message Anda jelas dan deskriptif.

Lisensi
Proyek ini dilisensikan di bawah MIT License.

Kontak
Jika ada pertanyaan atau masukan, silakan hubungi:

Nama: [Mustofa Firdaus]
Email: [mustofafirdaus01@gmail.com]


Anda bisa menyesuaikan bagian-bagian seperti URL repository, nama, email, dan detail lainnya sesuai dengan proyek Anda. Letakkan file README.md ini di root direktori proyek (pada level yang sama dengan `manage.py`). Setelah itu, commit dan push file README.md ke GitHub.
