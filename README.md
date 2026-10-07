# WebDev Competition 2026 - RSA Autentication Token Aplikasi Web

## Anggota Kelompok
| Nama | NRP |
|---|---|
| Tasya Aulia Darmawan | 5027241009 |
| Azaria Raissa Maulidinnisa | 5027241043 |
| Afriza Tristan Calendra Rajasa | 5027241104 |

Sistem registrasi dan pengumpulan tugas untuk WebDev Competition 2026. Platform ini menggunakan algoritma kriptografi RSA untuk memastikan pertukaran data (Auth Token) antara peserta dan server berjalan secara aman.

## Alur Sistem
* **Registrasi:** Peserta mendaftarkan tim melalui form UI.
* **Proses Token:** Server panitia membuat Auth Token, lalu melakukan **Enkripsi RSA**. Token terenkripsi ini diberikan untuk disimpan oleh peserta.
* **Akses Fitur:** Saat mengakses Dashboard/Form Pengumpulan, peserta mengirimkan token tersebut.
* **Verifikasi:** Server melakukan **Dekripsi RSA** terhadap token yang di-*input*. Jika valid, akses diberikan.

## Teknologi yang Digunakan
* **Front-End:** HTML5, CSS3, JavaScript, Bootstrap 5, Jinja2 Templates.
* **Back-End:** Python 3, Flask.
* **Database:** SQLite (via SQLAlchemy).

## Cara Menjalankan secara Lokal

1. Pastikan Python sudah terinstal di komputermu.
2. *Clone* repositori ini:
   ```bash
   git clone https://github.com/baksoogoreng/tugas-rsa.git
   ```
3. Masuk ke direktori proyek dan instal dependencies yang dibutuhkan:
    ```bash
   python app.py
   ```
4. Buka browser dan akses
    ```bash
   http://127.0.0.1:5000/
   ```