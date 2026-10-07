"""
token_service.py - Membuat & memverifikasi Auth Token peserta lomba.
Semua proses enkripsi/dekripsi memanggil fungsi RSA dari rsa.py.
"""

import json
import os
import time

import rsa

KEY_FILE = "keys.json"      # tempat menyimpan kunci server
TOKEN_PREFIX = "LOMBA"      # penanda bahwa token memang dibuat oleh server ini


def load_or_create_keys():
    """Memuat kunci dari keys.json; jika belum ada, buat baru lalu simpan."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            data = json.load(f)
        # Angka besar disimpan sebagai string, ubah kembali ke integer
        public_key = (int(data["public"][0]), int(data["public"][1]))
        private_key = (int(data["private"][0]), int(data["private"][1]))
        return public_key, private_key

    public_key, private_key = rsa.generate_keys(bits=64)
    data = {
        "public": [str(public_key[0]), str(public_key[1])],
        "private": [str(private_key[0]), str(private_key[1])],
    }
    with open(KEY_FILE, "w") as f:
        json.dump(data, f)
    return public_key, private_key


# Kunci dimuat sekali saat server dijalankan
PUBLIC_KEY, PRIVATE_KEY = load_or_create_keys()


def create_token(team_id, valid_hours=24):
    """Membuat token terenkripsi untuk sebuah tim (berlaku valid_hours jam)."""
    expiry = int(time.time()) + valid_hours * 3600      # waktu kedaluwarsa
    payload = f"{TOKEN_PREFIX}|{team_id}|{expiry}"      # isi token (teks biasa)
    return rsa.encrypt(payload, PUBLIC_KEY)             # disegel dengan RSA


def verify_token(token):
    """Memeriksa token. Mengembalikan (True, team_id) atau (False, alasan)."""
    # 1. Dekripsi token dengan private key
    try:
        payload = rsa.decrypt(token, PRIVATE_KEY)
    except ValueError:
        return False, "Token tidak valid"

    # 2. Cek format isi token: LOMBA|team_id|expiry
    parts = payload.split("|")
    if len(parts) != 3 or parts[0] != TOKEN_PREFIX:
        return False, "Token tidak valid"
    if not (parts[1].isdigit() and parts[2].isdigit()):
        return False, "Token tidak valid"

    # 3. Cek apakah token sudah kedaluwarsa
    if int(parts[2]) < time.time():
        return False, "Token sudah kedaluwarsa"

    # 4. Token sah, kembalikan ID tim
    return True, int(parts[1])