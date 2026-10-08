"""
test_rsa.py - Tes sederhana di terminal. Jalankan: python test_rsa.py
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


def test_tanda_tangan():
    """Tes: tanda tangan valid lolos, pesan yang diubah / tanda tangan salah gagal."""
    public_key, private_key = rsa.generate_keys(bits=64)
    sig = rsa.sign("LOMBA|7|123", private_key)
    assert rsa.verify("LOMBA|7|123", sig, public_key)
    assert not rsa.verify("LOMBA|8|123", sig, public_key)
    assert not rsa.verify("LOMBA|7|123", sig + 1, public_key)
    print("[OK] Tanda tangan valid lolos, pesan diubah / tanda tangan salah gagal")


def test_token_dipalsukan_dengan_public_key():
    """Tes: penyerang yang tahu PUBLIC KEY tetap tidak bisa membuat token sah."""
    # Tanpa tanda tangan
    palsu1 = rsa.encrypt("LOMBA|1|9999999999", token_service.PUBLIC_KEY)
    ok, alasan = token_service.verify_token(palsu1)
    assert not ok
    # Dengan tanda tangan karangan
    palsu2 = rsa.encrypt("LOMBA|1|9999999999|abc123", token_service.PUBLIC_KEY)
    ok, alasan = token_service.verify_token(palsu2)
    assert not ok
    print("[OK] Token palsu buatan penyerang (tahu public key) ditolak:", alasan)


if __name__ == "__main__":
    test_rsa_dasar()
    test_tanda_tangan()
    test_token_valid()
    test_token_kedaluwarsa()
    test_token_palsu()
    test_token_dipalsukan_dengan_public_key()
    print("\nSemua tes lulus.")