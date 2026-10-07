"""
database.py - Penyimpanan data tim & pengumpulan proyek (SQLite).
SQLite sudah bawaan Python, jadi tidak perlu install apa pun.
"""

import sqlite3
from datetime import datetime

DB_FILE = "lomba.db"   # nama file database


def get_connection():
    """Membuka koneksi ke database. Hasil query bisa diakses dengan nama kolom."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel teams dan submissions jika belum ada."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS teams (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name  TEXT NOT NULL UNIQUE,
            leader     TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            campus     TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS submissions (
            team_id      INTEGER PRIMARY KEY,
            project_url  TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def add_team(team_name, leader, email, campus):
    """Menyimpan tim baru dan mengembalikan ID-nya.
    Melempar sqlite3.IntegrityError jika nama tim / email sudah terdaftar."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO teams (team_name, leader, email, campus, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (team_name, leader, email, campus, now),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_team(team_id):
    """Mengambil data satu tim berdasarkan ID (None jika tidak ada)."""
    conn = get_connection()
    team = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
    conn.close()
    return team


def get_all_teams():
    """Mengambil semua tim beserta link proyeknya (untuk halaman admin)."""
    conn = get_connection()
    teams = conn.execute(
        "SELECT t.*, s.project_url FROM teams t "
        "LEFT JOIN submissions s ON s.team_id = t.id ORDER BY t.id"
    ).fetchall()
    conn.close()
    return teams


def save_submission(team_id, project_url):
    """Menyimpan link proyek tim. Jika sudah pernah submit, link lama ditimpa."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    conn.execute(
        "INSERT INTO submissions (team_id, project_url, submitted_at) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT(team_id) DO UPDATE SET "
        "project_url = excluded.project_url, submitted_at = excluded.submitted_at",
        (team_id, project_url, now),
    )
    conn.commit()
    conn.close()


def get_submission(team_id):
    """Mengambil link proyek milik tim (None jika belum submit)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM submissions WHERE team_id = ?", (team_id,)
    ).fetchone()
    conn.close()
    return row