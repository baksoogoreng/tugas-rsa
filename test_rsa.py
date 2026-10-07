"""
test_rsa.py - Tes sederhana di terminal. Jalankan: python3 test_rsa.py
"""

import rsa
import token_service


def test_rsa_dasar():
    """Tes: teks yang dienkripsi lalu didekripsi harus kembali sama."""
    public_key, private_key = rsa.generate_keys(bits=64)
    pesan = "Halo Kriptografi 123!"
    cipher = rsa.encrypt(pesan, public_key)
    hasil = rsa.decrypt(cipher, private_key)
    assert hasil == pesan
    print("[OK] Enkripsi -> dekripsi menghasilkan teks yang sama")


def test_token_valid():
    """Tes: token baru harus lolos verifikasi dan mengembalikan ID tim."""
    token = token_service.create_token(team_id=7)
    ok, hasil = token_service.verify_token(token)
    assert ok and hasil == 7
    print("[OK] Token valid diterima (team_id = 7)")


def test_token_kedaluwarsa():
    """Tes: token dengan masa berlaku negatif harus ditolak."""
    token = token_service.create_token(team_id=7, valid_hours=-1)
    ok, alasan = token_service.verify_token(token)
    assert not ok
    print("[OK] Token kedaluwarsa ditolak:", alasan)


def test_token_palsu():
    """Tes: token yang diubah/dikarang harus ditolak."""
    token = token_service.create_token(team_id=7)
    blocks = token.split("-")
    blocks[3] = blocks[3][:-1] + ("0" if blocks[3][-1] != "0" else "1")
    ok, alasan = token_service.verify_token("-".join(blocks))
    assert not ok
    print("[OK] Token yang diubah ditolak:", alasan)

    ok, alasan = token_service.verify_token("asal-ketik")
    assert not ok
    print("[OK] Token asal-asalan ditolak:", alasan)


if __name__ == "__main__":
    test_rsa_dasar()
    test_token_valid()
    test_token_kedaluwarsa()
    test_token_palsu()
    print("\nSemua tes lulus.")