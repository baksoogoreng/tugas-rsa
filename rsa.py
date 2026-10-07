"""
rsa.py - Implementasi RSA buatan sendiri (tanpa library kriptografi).
Hanya memakai modul bawaan Python: secrets (angka acak yang aman).
"""

import secrets

# Bilangan prima kecil untuk "penyaring cepat" sebelum uji Miller-Rabin
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def gcd(a, b):
    """Mencari FPB dua bilangan (algoritma Euclid). Dipakai untuk memilih e."""
    while b != 0:
        a, b = b, a % b
    return a


def mod_pow(base, exp, mod):
    """Menghitung (base^exp) mod mod dengan cepat (square-and-multiply)."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:              # bit terakhir exp = 1 -> kalikan hasil
            result = (result * base) % mod
        base = (base * base) % mod    # kuadratkan base
        exp = exp // 2                # geser ke bit berikutnya
    return result


def is_prime(n, rounds=20):
    """Mengecek apakah n bilangan prima (uji Miller-Rabin)."""
    if n < 2:
        return False
    for p in SMALL_PRIMES:            # saring cepat dengan prima kecil
        if n % p == 0:
            return n == p

    # Tulis n-1 = d * 2^r dengan d ganjil
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(rounds):           # ulangi uji dengan basis acak
        a = secrets.randbelow(n - 3) + 2
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False              # pasti bukan prima
    return True                       # kemungkinan besar prima


def generate_prime(bits):
    """Menghasilkan bilangan prima acak dengan panjang 'bits' bit (p atau q)."""
    while True:
        # Paksa bit paling atas = 1 (panjang pas) dan bit terakhir = 1 (ganjil)
        n = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n


def mod_inverse(e, phi):
    """Mencari d sehingga (e * d) mod phi = 1 (Extended Euclid)."""
    old_r, r = e, phi
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_s % phi


def generate_keys(bits=64):
    """Membuat pasangan kunci RSA. Mengembalikan (public_key, private_key)."""
    # 1. Pilih dua bilangan prima berbeda p dan q
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    # 2. Hitung n = p x q
    n = p * q

    # 3. Hitung phi(n) = (p-1)(q-1)
    phi = (p - 1) * (q - 1)

    # 4. Pilih e (umum dipakai 65537), pastikan FPB(e, phi) = 1
    e = 65537
    while gcd(e, phi) != 1:
        e += 2

    # 5. Hitung d = kebalikan modular dari e terhadap phi
    d = mod_inverse(e, phi)

    # 6. Public key = (e, n), Private key = (d, n)
    return (e, n), (d, n)


def encrypt(text, public_key):
    """Mengenkripsi teks: tiap karakter -> angka m -> c = m^e mod n.
    Hasilnya string hex per karakter, dipisah tanda '-'."""
    e, n = public_key
    blocks = []
    for ch in text:
        m = ord(ch)                   # karakter -> angka (harus < n)
        c = mod_pow(m, e, n)          # rumus enkripsi RSA
        blocks.append(format(c, "x")) # simpan sebagai hex agar lebih pendek
    return "-".join(blocks)


def decrypt(cipher_text, private_key):
    """Mendekripsi teks: tiap blok c -> m = c^d mod n -> karakter.
    Melempar ValueError jika cipher rusak/tidak valid."""
    d, n = private_key
    chars = []
    for block in cipher_text.split("-"):
        c = int(block, 16)            # hex -> angka (error jika format salah)
        m = mod_pow(c, d, n)          # rumus dekripsi RSA
        if m > 0x10FFFF:              # di luar rentang karakter -> cipher rusak
            raise ValueError("Cipher tidak valid")
        chars.append(chr(m))          # angka -> karakter
    return "".join(chars)