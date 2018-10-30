def long_range(start, stop, step=1):
    """
    Sequence generator working with python longs
    :param start: start of the range
    :param stop: end of the range (exclusive)
    :param step: step
    :return: sequence of numbers
    """
    i = start
    while i < stop:
        yield i
        i += step


def bytes_to_long(data):
    """
    Convert byte string to integer
    :param data: byte string
    :return: integer
    """
    try:
        return int.from_bytes(data, 'big')
    except TypeError:
        return bytes_to_long(data.encode('utf-8'))
    except AttributeError:
        return int(data.encode('hex'), 16)


def long_to_bytes(data):
    """
    Convert integer to string.
    This function is NOT safe for multi-byte characters!
    If you're decoding some UTF data use the function from pycrypto.
    :param data: integer
    :return: ascii encoded string
    """
    data = int(data)
    data = hex(data).rstrip('L').lstrip('0x')
    if len(data) % 2 == 1:
        data = '0' + data
    return bytes(bytearray(int(c, 16) for c in chunk(data, 2)))


def chunk(input_data, size):
    """
    Chunk given bytes into parts
    :param input_data: bytes to split
    :param size: size of a single chunk
    :return: list of chunks
    """
    assert len(input_data) % size == 0, \
        "can't split data into chunks of equal size, try using chunk_with_remainder or pad data"
    return [input_data[i:i + size] for i in range(0, len(input_data), size)]


def chunk_with_remainder(input_data, size):
    """
    Chunk given bytes into parts, with the possibility of last chunk not full
    :param input_data: bytes to split
    :param size: size of a single full chunk
    :return: list of chunks
    """
    if len(input_data) % size == 0:
        return chunk(input_data, size)
    else:
        remainder_start = -(len(input_data) % size)
        core = input_data[:remainder_start]
        remainder = input_data[remainder_start:]
        return chunk(core, size) + [remainder]


def multiply(values):
    """
    Multiply values on the list
    :param values: list of values
    :return: a*b*c*d...
    """
    import functools
    return functools.reduce(lambda x, y: x * y, values, 1)


def factorial(n):
    """
    Return factorial of n
    :param n: number
    :return: n!
    """

    import math
    return math.factorial(n)


def get_primes(limit=1000000):
    """
    Use sieve to get list of prime numbers in range
    :param limit: range for search
    :return: list of primes in range
    """
    m = limit + 1
    numbers = [True for _ in long_range(0, m)]
    for i in long_range(2, int(limit ** 0.5)):
        if numbers[i]:
            for j in long_range(i * i, m, i):
                numbers[j] = False
    primes = [i for i in long_range(2, m) if numbers[i]]
    return primes


def factor_p(n, primes, limit=1000000):
    """
    Factor given value using sieve up to a certain limit
    :param n: number to factor
    :param limit: sieve limit
    :return: list of factors and residue
    """
    factors = []
    for prime in primes:
        while n % prime == 0 and n > 2:
            n //= prime
            factors.append(prime)
        if n < 2:
            break
    else:
        if n < limit ** 2:
            factors.append(n)
            n = 1
    return factors, n


def factor(n, limit=1000000):
    """
    Factor given value using sieve up to a certain limit
    :param n: number to factor
    :param limit: sieve limit
    :return: list of factors and residue
    """
    return factor_p(n, get_primes(limit), limit)


def fermat_factors(n):
    """
    Factor given number using Fermat approach, starting from sqrt(n)
    :param n: modulus to factor
    :return: p, q
    """
    assert n % 2 != 0
    import gmpy2
    a = gmpy2.isqrt(n)
    b2 = gmpy2.square(a) - n
    while not gmpy2.is_square(b2):
        a += 1
        b2 = gmpy2.square(a) - n
    factor1 = a + gmpy2.isqrt(b2)
    factor2 = a - gmpy2.isqrt(b2)
    print(n, factor1, factor2)
    return int(factor1), int(factor2)


def find_divisor(n, limit=1000000):
    """
    Use sieve to find first prime divisor of given number
    :param n: number
    :param limit: sieve limit
    :return: prime divisor if exists in sieve limit
    """
    primes = get_primes(limit)
    for prime in primes:
        if n % prime == 0:
            return prime
    raise (Exception("No divisors found in range %d" % limit))


def integer_log(x, xi, limit=1000):
    """
    Computation of integer logarithm.
    For x and x^i returns exponent i if such i exists.
    :param x: base
    :param xi: power value
    :param limit: search limit
    :return: exponent
    """
    if xi == 1:
        return 0
    for i in range(limit):
        xi, r = divmod(xi, x)
        if xi == 1:
            return i + 1
        if r > 0:
            return


def discrete_log(x, xi, limit=1000):
    """
    Alias for integer_log added for backwards compability.
    Computation of integer logarithm.
    For x and x^i returns exponent i if such i exists.
    :param x: base
    :param xi: power value
    :param limit: search limit
    :return: exponent
    """
    return integer_log(x, xi, limit)


def xor(*t):
    """
    XOR variable number of arrays with integers
    :param *t: arrays 
    :return: list with xored values
    """
    from functools import reduce
    from operator import xor
    return [reduce(xor, x, 0) for x in zip(*t)]


def xor_string(t1, t2):
    """
    XOR two strings
    If both are Python3 bytes objects, use xor(t1, t2) instead.
    :param t1: string 1
    :param t2: string 2
    :return: string with xored values
    """

    t1 = map(ord, t1)
    t2 = map(ord, t2)

    return "".join(map(chr, xor(t1, t2)))


def xor_hex(t1, t2):
    """
    XOR two hex strings
    :param t1: string 1
    :param t2: string 2
    :return: xored hex string
    """
    import codecs
    t1 = codecs.decode(t1, "hex")
    t2 = codecs.decode(t2, "hex")

    try:
        xored = xor_string(t1, t2)
    except TypeError:
        xored = bytes(xor(t1, t2))
    return codecs.encode(xored, "hex")


def is_printable(data):
    import string
    printable = set(string.printable).union(string.printable.encode('utf-8'))
    return len(set(data).difference(printable)) == 0
