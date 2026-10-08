# WebDev Competition 2026 - RSA Authentication Token Aplikasi Web

## Anggota Kelompok
| Nama | NRP |
|---|---|
| Tasya Aulia Darmawan | 5027241009 |
| Azaria Raissa Maulidinnisa | 5027241043 |
| Afriza Tristan Calendra Rajasa | 5027241104 |

Sistem registrasi dan pengumpulan tugas untuk WebDev Competition 2026.  Sistem ini memanfaatkan algoritma RSA untuk melindungi Auth Token peserta. Setelah tim berhasil mendaftar, server panitia membuat token berisi identitas tim dan waktu kedaluwarsa, lalu mengenkripsinya menggunakan public key. Token terenkripsi tersebut disimpan oleh peserta dan dikirim kembali setiap kali peserta mengakses fitur tertentu. Server kemudian mendekripsi token menggunakan private key, memeriksa format dan masa berlakunya, serta memastikan tim tersebut terdaftar sebelum memberikan akses.

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
   pip install flask
   ```
4. Run
    ```bash
   python app.py
   ```
5. Buka browser dan akses
    ```bash
   http://127.0.0.1:5000/
   ```

## Note

Implementasi ini bertujuan sebagai media pembelajaran, bukan sistem autentikasi siap produksi. Beberapa batasannya adalah sebagai berikut: 

a) Kunci RSA yang digunakan hanya berukuran sekitar 128 bit agar proses demonstrasi cepat, padahal praktik nyata menggunakan minimal 2048 bit.

b) Enkripsi dilakukan per karakter tanpa skema padding, sehingga karakter yang sama selalu menghasilkan ciphertext yang sama. Akibatnya, pihak yang memiliki beberapa token sah secara teori dapat menyusun token baru dari blok-blok tersebut. Kelemahan ini dapat diatasi dengan tanda tangan digital dan skema padding.

c) Token hanya dienkripsi dan tidak ditandatangani; keamanannya bergantung pada kerahasiaan public key, padahal secara konsep public key boleh diketahui siapa saja.

Sebagai pengembangan lanjutan, token dapat ditandatangani secara digital menggunakan private key dan diverifikasi menggunakan public key, seperti pada JWT dengan algoritma RS256. Dengan demikian, keaslian dan integritas token dapat diverifikasi meskipun public key dapat diketahui oleh publik. Selain itu, keamanan implementasi dapat ditingkatkan dengan menggunakan ukuran kunci yang lebih besar, skema padding yang sesuai seperti RSA-PSS, serta pustaka kriptografi yang telah teruji.