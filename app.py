"""
app.py - Backend web (Flask) untuk pendaftaran & akses fitur lomba.
Token dibuat/diverifikasi lewat token_service.py (yang memakai RSA dari rsa.py).
"""

import os
import sqlite3
from functools import wraps

from flask import (Flask, Response, flash, g, make_response, redirect,
                   render_template, request, url_for)

import database
import token_service

app = Flask(__name__)
app.secret_key = "ganti-dengan-kunci-rahasia-sendiri"   # dipakai untuk pesan flash

COOKIE_NAME = "auth_token"   # nama cookie penyimpan token di browser peserta
TOKEN_HOURS = 24*14             # masa berlaku token 2 minggu
ADMIN_USER = "admin"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# Data pengumuman (statis agar sederhana)
ANNOUNCEMENTS = [
    {"date": "1 Nov 2026", "title": "Pendaftaran Ditutup",
     "body": "Pendaftaran tim ditutup pukul 23.59 WIB."},
    {"date": "5 Nov 2026", "title": "Technical Meeting",
     "body": "Technical meeting via Zoom, link dikirim ke email ketua tim."},
    {"date": "10 Nov 2026", "title": "Pengumpulan Proyek",
     "body": "Batas akhir mengumpulkan link proyek pukul 12.00 WIB."},
]

database.init_db()   # buat tabel saat aplikasi dijalankan


# ---------------------------------------------------------------
# Fungsi bantu: ambil & verifikasi token
# ---------------------------------------------------------------

def get_token_from_request():
    """Mengambil token dari header 'Authorization: Bearer ...' atau dari cookie."""
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    return request.cookies.get(COOKIE_NAME)


def check_request_token():
    """Memverifikasi token pada request. Mengembalikan (data_tim, pesan_error)."""
    if "auth_result" in g:                       # sudah pernah dicek di request ini
        return g.auth_result

    token = get_token_from_request()
    if not token:
        result = (None, "Silakan login dengan token Anda terlebih dahulu")
    else:
        ok, hasil = token_service.verify_token(token)   # dekripsi RSA terjadi di sini
        if not ok:
            result = (None, hasil)
        else:
            team = database.get_team(hasil)             # hasil = ID tim
            result = (team, None) if team else (None, "Tim tidak ditemukan")

    g.auth_result = result
    return result


def token_required(view):
    """Decorator: halaman hanya bisa dibuka jika token valid."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        team, error = check_request_token()
        if team is None:
            flash(error, "error")
            response = redirect(url_for("login"))
            response.delete_cookie(COOKIE_NAME)         # buang token yang tidak sah
            return response
        g.team = team
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    """Decorator: halaman admin dilindungi username & password (HTTP Basic)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USER or auth.password != ADMIN_PASSWORD:
            return Response("Login admin diperlukan", 401,
                            {"WWW-Authenticate": 'Basic realm="Admin"'})
        return view(*args, **kwargs)
    return wrapper


def set_token_cookie(response, token):
    """Menyimpan token ke cookie browser (HttpOnly agar tidak dibaca JavaScript)."""
    response.set_cookie(COOKIE_NAME, token, max_age=TOKEN_HOURS * 3600,
                        httponly=True, samesite="Lax")
    return response


@app.context_processor
def inject_current_team():
    """Mengirim 'current_team' ke semua template (untuk navbar: sudah login atau belum)."""
    team, _ = check_request_token()
    return {"current_team": team}


# ---------------------------------------------------------------
# Halaman publik
# ---------------------------------------------------------------

@app.route("/")
def index():
    """Halaman utama (landing page)."""
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registrasi tim. Jika berhasil: buat token terenkripsi RSA lalu simpan di cookie."""
    if request.method == "GET":
        return render_template("register.html", form={})

    # Ambil & bersihkan input form
    team_name = request.form.get("team_name", "").strip()
    leader = request.form.get("leader", "").strip()
    email = request.form.get("email", "").strip().lower()
    campus = request.form.get("campus", "").strip()

    # Validasi sederhana
    error = None
    if not (3 <= len(team_name) <= 50):
        error = "Nama tim harus 3-50 karakter"
    elif not leader or not campus:
        error = "Nama ketua dan asal kampus wajib diisi"
    elif "@" not in email or "." not in email:
        error = "Format email tidak valid"

    if error:
        flash(error, "error")
        return render_template("register.html", form=request.form)

    # Simpan tim ke database
    try:
        team_id = database.add_team(team_name, leader, email, campus)
    except sqlite3.IntegrityError:
        flash("Nama tim atau email sudah terdaftar", "error")
        return render_template("register.html", form=request.form)

    # Buat token (dienkripsi RSA) lalu kirim ke peserta lewat cookie
    token = token_service.create_token(team_id, TOKEN_HOURS)
    flash("Registrasi berhasil! Simpan token Anda.", "success")
    return set_token_cookie(make_response(redirect(url_for("token_page"))), token)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login dengan menempelkan token (untuk peserta yang cookie-nya hilang)."""
    if request.method == "GET":
        return render_template("login.html")

    # Token hasil copy-paste bisa mengandung spasi/baris baru, hapus semuanya
    token = "".join(request.form.get("token", "").split())
    ok, hasil = token_service.verify_token(token)
    if not ok:
        flash(hasil, "error")
        return render_template("login.html")

    if database.get_team(hasil) is None:
        flash("Tim tidak ditemukan", "error")
        return render_template("login.html")

    flash("Login berhasil", "success")
    return set_token_cookie(make_response(redirect(url_for("dashboard"))), token)


@app.route("/logout")
def logout():
    """Keluar: hapus cookie token dari browser."""
    response = make_response(redirect(url_for("index")))
    response.delete_cookie(COOKIE_NAME)
    return response


# ---------------------------------------------------------------
# Halaman peserta (wajib token valid)
# ---------------------------------------------------------------

@app.route("/token")
@token_required
def token_page():
    """Menampilkan token terenkripsi milik tim (untuk disalin peserta)."""
    return render_template("token.html", team=g.team,
                           token=get_token_from_request())


@app.route("/dashboard")
@token_required
def dashboard():
    """Dashboard tim: info tim dan status pengumpulan proyek."""
    submission = database.get_submission(g.team["id"])
    return render_template("dashboard.html", team=g.team, submission=submission)


@app.route("/submit", methods=["GET", "POST"])
@token_required
def submit():
    """Form pengumpulan link proyek (GitHub / hosting)."""
    if request.method == "POST":
        url = request.form.get("project_url", "").strip()
        if not url.startswith(("http://", "https://")) or len(url) > 300:
            flash("Link harus diawali http:// atau https://", "error")
        else:
            database.save_submission(g.team["id"], url)
            flash("Proyek berhasil dikumpulkan", "success")
            return redirect(url_for("submit"))

    submission = database.get_submission(g.team["id"])
    return render_template("submit.html", team=g.team, submission=submission)


@app.route("/announcements")
@token_required
def announcements():
    """Pengumuman lomba (hanya untuk peserta terdaftar)."""
    return render_template("announcements.html", team=g.team,
                           announcements=ANNOUNCEMENTS)


# ---------------------------------------------------------------
# Halaman admin
# ---------------------------------------------------------------

@app.route("/admin")
@admin_required
def admin():
    """Daftar semua tim terdaftar beserta link proyeknya."""
    return render_template("admin.html", teams=database.get_all_teams())


if __name__ == "__main__":
    app.run(debug=True)