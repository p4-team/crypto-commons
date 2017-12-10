import random

from crypto_commons.generic import long_to_bytes, multiply, factorial
from crypto_commons.rsa.rsa_commons import ensure_long, modinv, lcm_multi

"""
Here are some less popular asymmetric cryptosystems:
- Damgard-Jurik
- Paillier (same as Damgard Jurik for s = 1)
"""


def paillier_encrypt(m, g, n, r):
    """
    Encrypt data using Paillier Cryptosystem
    Actually it's the same as Damgard Jurik with s=1
    :param m:  plaintext to encrypt, can be either long or bytes
    :param g: random public integer g
    :param n: modulus
    :param r: random r
    :return: encrypted data as long
    """
    m = ensure_long(m)
    n2 = n * n
    return (pow(g, m, n2) * pow(r, n, n2)) % n2


def paillier_encrypt_simple(m, g, n):
    """
    Encrypt data using Paillier Cryptosystem
    Actually it's the same as Damgard Jurik with s=1
    :param m:  plaintext to encrypt, can be either long or bytes
    :param g: random public integer g
    :param n: modulus
    :return: encrypted data as long
    """
    n2 = n * n
    r = random.randint(2, n2)
    return paillier_encrypt(m, g, n, r)


def paillier_decrypt(c, factors, g):
    """
    Decrypt data using Paillier Cryptosystem
    Actually it's the same as Damgard Jurik with s=1
    :param c: ciphertext
    :param factors: prime factors
    :param g: random public integer g
    :return: decrypted data as long
    """

    def L(u, n):
        return int((u - 1) // n)

    lbd = lcm_multi([p - 1 for p in factors])
    n = multiply(factors)
    x = L(pow(g, lbd, n * n), n)
    mi = int(modinv(x, n))
    m = L(pow(c, lbd, n * n), n) * pow(mi, 1, n)
    return m % n


def paillier_decrypt_printable(c, factors, g):
    """
    Decrypt data using Paillier Cryptosystem
    Actually it's the same as Damgard Jurik with s=1
    :param c: ciphertext
    :param factors: prime factors
    :param g: random public integer g
    :return: decrypted data as bytes
    """
    return long_to_bytes(paillier_decrypt(c, factors, g))


def damgard_jurik_encrypt(m, n, g, s):
    """
    Encrypt data using Damgard Jurik Cryptosystem
    :param m: plaintext
    :param n: modulus
    :param g: random public integer g
    :param s: order n^s
    :return:
    """
    m = ensure_long(m)
    s1 = s + 1
    ns1 = n ** s1
    r = random.randint(2, ns1)
    enc = pow(g, m, ns1) * pow(r, n ** s, ns1) % ns1
    return enc


def damgard_jurik_decrypt(c, n, s, factors, g):
    """
    Decrypt data using Damgard Jurik Cryptosystem
    :param c: ciphertext
    :param n: modulus
    :param s: order n^s
    :param factors: modulus prime factors
    :param g: random public integer g
    :return:
    """

    def decrypt(ct, d, n, s):
        def L(x):
            return (x - 1) / n

        ns1 = pow(n, s + 1)
        a = pow(ct, d, ns1)
        i = 0
        for j in range(1, s + 1):
            t1 = L(a % pow(n, j + 1))
            t2 = i
            for k in range(2, j + 1):
                i -= 1
                t2 = (t2 * i) % pow(n, j)
                fac = long(factorial(k))
                up = (t2 * pow(n, k - 1))
                down = modinv(fac, pow(n, j))
                t1 = (t1 - up * down) % pow(n, j)
            i = t1
        return i

    d = lcm_multi([p - 1 for p in factors])
    ns = pow(n, s)
    jd = decrypt(g, d, n, s)
    jd_inv = modinv(jd, ns)
    jmd = decrypt(c, d, n, s)
    return (jd_inv * jmd) % ns
