from functools import reduce
from crypto_commons.generic import bytes_to_long, find_divisor, multiply, long_to_bytes


def rsa_printable(x, exp, n):
    """
    Calculate RSA encryption/decryption and return result as bytes
    :param x: plaintex or ciphertext, can be either bytes or int
    :param exp: exponent
    :param n: modulus
    :return: result bytes
    """
    return long_to_bytes(rsa(x, exp, n))


def rsa(x, exp, n):
    """
    Calculate RSA encryption/decryption and return result as int 
    :param x: plaintex or ciphertext, can be either bytes or int
    :param exp: exponent
    :param n: modulus
    :return: result int
    """
    return pow(ensure_long(x), exp, n)


def recover_factors_from_phi(n, phi):
    """
    For n = p*q and phi = (p-1)*(q-1), recover p and q as ints
    Both p and q need to be prime
    :param n: int
    :param phi: int
    :return: result pair of ints (p, q), sorted
    """
    from gmpy2 import isqrt
    p_plus_q = n - phi + 1
    delta = p_plus_q**2 - 4*n
    p = int((p_plus_q + isqrt(delta)) // 2)
    q = int(n // p)

    if p*q != n or (p-1)*(q-1) != phi:
        raise ValueError("n is not a product of two primes"
                         ", or phi is not it's totient")

    return tuple(sorted((p, q)))


def ensure_long(x):
    try:
        return bytes_to_long(x)
    except AttributeError:
        return x


def solve_crt(residue_and_moduli):
    """
    Solve CRT for given modular residues and modulus values, eg:
    x = 1 mod 3
    x = 2 mod 4
    x = 3 mod 5
    x = 58
    residue_and_moduli = [(1,3), (2,4), (3,5)]
    :param residue_and_moduli: list of pairs with (modular residue mod n, n)
    :return: x
    """
    residues, moduli = zip(*residue_and_moduli)
    N = multiply(moduli)
    Nxs = [N // n for n in moduli]
    ds = [modinv(N // n, n) for n in moduli]
    mults = [r * Nx * d for r, Nx, d in zip(residues, Nxs, ds)]
    return reduce(lambda x, y: x + y, mults) % N


def get_fi_distinct_primes(primes):
    """
    Get Euler totient for list of pairwise co-prime numbers
    :param primes: list of co-prime numbers
    :return: fi(n) = (p-1)(q-1)...
    """
    return multiply((p - 1) for p in primes)


def get_fi_repeated_prime(p, k=1):
    """
    Return Euler totient for prime power p^k
    :param p: prime number
    :param k: power
    :return: fi(p^k)
    """
    return pow(p, k - 1) * (p - 1)


def extended_gcd(a, b):
    """
    Calculate extended greatest common divisor of numbers a,b
    :param a: first number
    :param b: second number
    :return: gcd(a,b) and remainders
    """

    def copysign(a, b):
        return a * (1 if b >= 0 else -1)

    lastrem, rem = abs(a), abs(b)
    x, lastx, y, lasty = 0, 1, 1, 0
    while rem:
        lastrem, (quotient, rem) = rem, divmod(lastrem, rem)
        x, lastx = lastx - quotient * x, x
        y, lasty = lasty - quotient * y, y
    return lastrem, copysign(lastx, a), copysign(lasty, b)


def gcd(a, b):
    """
    Return simple greatest common divisor of a and b
    :param a:
    :param b:
    :return: gcd(a,b)
    """
    return extended_gcd(a, b)[0]


def gcd_multi(numbers):
    """
    Calculate gcd for the list of numbers
    :param numbers: list of numbers
    :return: gcd(a,b,c,d,...)
    """
    from functools import reduce
    return reduce(gcd, numbers)


def lcm(a, b):
    """
    Calculate least common multiple of a,b
    :param a: first number
    :param b: second number
    :return: lcm(a,b)
    """
    return a * (b // gcd(a, b))


def lcm_multi(numbers):
    """
    Calculate lcm for the list of numbers
    :param numbers: list of numbers
    :return: lcm(a,b,c,d,...)
    """
    return reduce(lcm, numbers)


def modinv(x, y):
    """
    Return modular multiplicative inverse of x mod y.
    It is a value d such that x*d = 1 mod y
    :param x: number for which we want inverse
    :param y: modulus
    :return: modinv if it exists
    """
    return extended_gcd(x, y)[1] % y


def rsa_crt_distinct_multiprime(c, e, factors):
    """
    Calculate RSA-CRT solution. For c = pt^e mod n returns pt.
    n = factors[0]*factors[1]*... and each factor has to be relatively prime
    :param c: ciphertext
    :param e: public exponent
    :param factors: modulus factors
    :return: decoded ciphertext
    """
    k = len(factors)
    di = [modinv(e, prime - 1) for prime in factors]
    m = factors[0]
    tis = [-1]
    for prime in factors[1:]:
        tis.append(modinv(m, prime))
        m = m * prime
    y = c
    xis = []
    for i in range(k):
        xis.append(pow(y, di[i], factors[i]))
    x = xis[0]
    m = factors[0]
    for i in range(1, k):
        ri = factors[i]
        xi = xis[i]
        ti = tis[i]
        x += m * (((xi - x % ri) * ti) % ri)
        m = m * ri
    return x


def lift(f, df, p, k, previous):
    result = []
    for lower_solution in previous:
        dfr = df(lower_solution)
        fr = f(lower_solution)
        if dfr % p != 0:
            t = (-(extended_gcd(dfr, p)[1]) * int(fr / p ** (k - 1))) % p
            result.append(lower_solution + t * p ** (k - 1))
        if dfr % p == 0:
            if fr % p ** k == 0:
                for t in range(0, p):
                    result.append(lower_solution + t * p ** (k - 1))
    return result


def hensel_lifting(f, df, p, k, base_solution):
    """
    Calculate solutions to f(x) = 0 mod p^k for prime p
    :param f: function
    :param df: derivative
    :param p: prime
    :param k: power
    :param base_solution: solution to return for p=1
    :return: possible solutions to f(x) = 0 mod p^k
    """
    if type(base_solution) is list:
        solution = base_solution
    else:
        solution = [base_solution]
    for i in range(2, k + 1):
        solution = lift(f, df, p, i, solution)
    return solution


def hastad_broadcast(residue_and_moduli):
    """
    Hastad RSA attack for the same message encrypted with the same public exponent e and different modulus.
    Requires exactly 'e' pairs as input
    Depends on gmpy2 because I don't know how to write a fast k-th integer root.
    :param residue_and_moduli: list of pairs (residue, modulus)
    :return: decrypted message
    """
    import gmpy2
    k = len(residue_and_moduli)
    solution, _ = gmpy2.iroot(solve_crt(residue_and_moduli), k)
    assert residue_and_moduli[0][0] == pow(int(solution), k, residue_and_moduli[0][1])
    return solution


def combine_signatures(signatures, N):
    return multiply(signatures) % N


def homomorphic_blinding_rsa(payload, get_signature, N, splits=2):
    """
    Perform blinding RSA attack on non-padded homomorphic implementations.
    It will use the signature service multiple times to get final signature.
    :param payload: data to sign
    :param get_signature: function returning signature
    :param N: modulus
    :param splits: on how many parts the data should be split
    :return: signed data
    """
    data = ensure_long(payload)
    parts = []
    for i in range(splits):
        smallest_divisor = find_divisor(data)
        parts.append(smallest_divisor)
        data = data // smallest_divisor
    parts.append(data)
    signatures = [get_signature(value) for value in parts]
    result_sig = combine_signatures(signatures, N)
    return result_sig


def modular_sqrt_composite(c, p, q):
    """
    Calculates modular square root of composite value for given 2 factors
    For a = b^2 mod p*q calculates b
    :param a: residue
    :param p: modulus prime factor
    :param q: modulus prime factor
    :return: 4 potential root values
    """
    n = p * q
    gcd_value, yp, yq = extended_gcd(p, q)
    mp = modular_sqrt(c, p)
    mq = modular_sqrt(c, q)
    assert yp * p + yq * q == 1
    assert (mp * mp) % p == c % p
    assert (mq * mq) % q == c % q
    r1 = (yp * p * mq + yq * q * mp) % n
    s1 = (yp * p * mq - yq * q * mp) % n
    r2 = n - r1
    s2 = n - s1
    return r1, s1, r2, s2


def modular_sqrt(a, p):
    """
    Calculates modular square root with prime modulus.
    For a = b^2 mod p calculates b
    :param a: residue
    :param p: modulus
    :return: root value
    """
    if legendre_symbol(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return p
    elif p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    s = p - 1
    e = 0
    while s % 2 == 0:
        s /= 2
        e += 1
    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1
    x = pow(a, (s + 1) // 2, p)
    b = pow(a, s, p)
    g = pow(n, s, p)
    r = e
    while True:
        t = b
        m = 0
        for m in xrange(r):
            if t == 1:
                break
            t = pow(t, 2, p)
        if m == 0:
            return x
        gs = pow(g, 2 ** (r - m - 1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def legendre_symbol(a, p):
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls


def common_factor_factorization(ns):
    """
    Try to factor given list of moduli by calculating gcd for each pair, hoping that some share the same prime
    :param ns: list of moduli
    :return: list of triplets (modulus1, modulus2, shared prime)
    """
    from itertools import combinations
    return [(n1, n2, gcd(n1, n2)) for n1, n2 in combinations(ns, 2) if gcd(n1, n2) != 1]
