"""
test_app.py - Tes backend Flask. Jalankan: python test_app.py
Memakai template tiruan (stub) sehingga bisa dijalankan sebelum UI dari Orang 3 jadi.
Database yang dipakai adalah file sementara, bukan lomba.db yang asli.
"""

import base64
import os
import tempfile

from jinja2 import DictLoader

import database

# Arahkan database ke file sementara SEBELUM app diimpor
database.DB_FILE = os.path.join(tempfile.mkdtemp(), "test.db")

import app as app_module
import token_service

# Template tiruan: cukup menampilkan data yang dikirim backend
FLASH = "{% for c, m in get_flashed_messages(with_categories=true) %}[{{ m }}]{% endfor %}"
app_module.app.jinja_env.loader = DictLoader({
    "landing.html": "LANDING " + FLASH,
    "register.html": "REGISTER " + FLASH,
    "login.html": "LOGIN " + FLASH,
    "token.html": "TOKEN {{ token }} " + FLASH,
    "dashboard.html": "DASHBOARD {{ team.team_name }} {{ submission.project_url if submission }} " + FLASH,
    "submit.html": "SUBMIT {{ submission.project_url if submission }} " + FLASH,
    "announcements.html": "ANNOUNCEMENTS {{ announcements|length }}",
    "admin.html": "ADMIN {% for t in teams %}{{ t.team_name }};{% endfor %}",
})
app_module.app.config["TESTING"] = True

FORM = {"team_name": "Tim Alpha", "leader": "Budi",
        "email": "alpha@mail.com", "campus": "ITS"}


def cookie_header(token):
    """Membuat header Cookie berisi token (meniru browser peserta)."""
    return {"Cookie": f"auth_token={token}"}


def test_halaman_publik():
    """Tes: landing, register, login bisa dibuka tanpa token."""
    c = app_module.app.test_client()
    for path in ["/", "/register", "/login"]:
        assert c.get(path).status_code == 200
    print("[OK] Halaman publik bisa dibuka")


def test_registrasi_dan_akses():
    """Tes: registrasi -> dapat token -> bisa akses halaman peserta."""
    c = app_module.app.test_client()
    r = c.post("/register", data=FORM)
    assert r.status_code == 302 and r.location.endswith("/token")
    assert "auth_token=" in r.headers["Set-Cookie"]

    assert "TOKEN " in c.get("/token").get_data(as_text=True)
    assert "Tim Alpha" in c.get("/dashboard").get_data(as_text=True)
    assert "ANNOUNCEMENTS 3" in c.get("/announcements").get_data(as_text=True)
    print("[OK] Registrasi menghasilkan token & halaman peserta bisa diakses")


def test_submit_proyek():
    """Tes: link proyek valid tersimpan, link tidak valid ditolak."""
    c = app_module.app.test_client()
    c.post("/register", data={**FORM, "team_name": "Tim Beta", "email": "beta@mail.com"})

    c.post("/submit", data={"project_url": "javascript:alert(1)"})
    assert "SUBMIT  " in c.get("/submit").get_data(as_text=True).replace("[", " ")[:20] + "  " \
        or "github" not in c.get("/submit").get_data(as_text=True)

    c.post("/submit", data={"project_url": "https://github.com/beta/web"})
    assert "https://github.com/beta/web" in c.get("/submit").get_data(as_text=True)
    print("[OK] Submit proyek: link valid disimpan, link berbahaya ditolak")


def test_tanpa_token_ditolak():
    """Tes: tanpa token, halaman peserta dialihkan ke /login."""
    c = app_module.app.test_client()
    for path in ["/token", "/dashboard", "/submit", "/announcements"]:
        r = c.get(path)
        assert r.status_code == 302 and r.location.endswith("/login")
    print("[OK] Tanpa token -> dialihkan ke login")


def test_token_palsu_dan_kedaluwarsa():
    """Tes: token diubah / asal ketik / kedaluwarsa ditolak."""
    c = app_module.app.test_client()
    c.post("/register", data={**FORM, "team_name": "Tim Gamma", "email": "g@mail.com"})
    token = c.get("/token").get_data(as_text=True).split()[1]

    blocks = token.split("-")
    blocks[2] = blocks[2][:-1] + ("0" if blocks[2][-1] != "0" else "1")
    palsu = "-".join(blocks)
    r = app_module.app.test_client().get("/dashboard", headers=cookie_header(palsu))
    assert r.status_code == 302 and r.location.endswith("/login")

    r = app_module.app.test_client().get("/dashboard", headers=cookie_header("asal-ketik"))
    assert r.status_code == 302

    kedaluwarsa = token_service.create_token(1, valid_hours=-1)
    r = app_module.app.test_client().get("/dashboard", headers=cookie_header(kedaluwarsa))
    assert r.status_code == 302
    print("[OK] Token palsu, asal-asalan, dan kedaluwarsa ditolak")


def test_header_bearer_dan_login():
    """Tes: token bisa dikirim lewat header Bearer, dan login dengan paste token."""
    c = app_module.app.test_client()
    c.post("/register", data={**FORM, "team_name": "Tim Delta", "email": "d@mail.com"})
    token = c.get("/token").get_data(as_text=True).split()[1]

    r = app_module.app.test_client().get(
        "/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200 and "Tim Delta" in r.get_data(as_text=True)

    baru = app_module.app.test_client()
    r = baru.post("/login", data={"token": token[:20] + "\n" + token[20:]})  # ada baris baru
    assert r.status_code == 302 and r.location.endswith("/dashboard")
    print("[OK] Header Bearer & login dengan paste token berhasil")


def test_registrasi_duplikat_dan_input_salah():
    """Tes: nama tim/email kembar dan input tidak valid ditolak."""
    c = app_module.app.test_client()
    r = c.post("/register", data=FORM)           # Tim Alpha sudah ada
    assert r.status_code == 200 and "sudah terdaftar" in r.get_data(as_text=True)
    r = c.post("/register", data={**FORM, "team_name": "ab"})
    assert "Nama tim" in r.get_data(as_text=True)
    r = c.post("/register", data={**FORM, "team_name": "Tim X", "email": "bukanemail"})
    assert "email" in r.get_data(as_text=True).lower()
    print("[OK] Duplikat & input tidak valid ditolak")


def test_admin():
    """Tes: halaman admin butuh username & password."""
    c = app_module.app.test_client()
    assert c.get("/admin").status_code == 401
    salah = base64.b64encode(b"admin:salah").decode()
    assert c.get("/admin", headers={"Authorization": f"Basic {salah}"}).status_code == 401

    benar = base64.b64encode(f"admin:{app_module.ADMIN_PASSWORD}".encode()).decode()
    r = c.get("/admin", headers={"Authorization": f"Basic {benar}"})
    assert r.status_code == 200 and "Tim Alpha" in r.get_data(as_text=True)
    print("[OK] Halaman admin terlindungi password")


if __name__ == "__main__":
    test_halaman_publik()
    test_registrasi_dan_akses()
    test_submit_proyek()
    test_tanpa_token_ditolak()
    test_token_palsu_dan_kedaluwarsa()
    test_header_bearer_dan_login()
    test_registrasi_duplikat_dan_input_salah()
    test_admin()
    print("\nSemua tes lulus.")