import functools
import gmpy2
from multiprocessing import freeze_support
from random import getrandbits

from crypto_commons.brute.brute import brute
from crypto_commons.generic import chunk_with_remainder, bytes_to_long, long_to_bytes


def hastad_attack_parallel(residue_and_moduli, e, parallel=6, major_chunk_size=1200, minor_chunk_size=120):
    """
    Calculate Hastad broadcast attack using Chinese Remainder Theorem using parallel solver.
    The more parallel processes you choose, the faster it will run, assuming you have enough CPU cores.
    The bigger the chunks, the faster it will run, but it will also consume more memory.
    Memory consumption is maximum once minor chunks start to process, so if you reached this stage without swapping, you should be fine.
    :param residue_and_moduli: list of pairs (remainder, modulus)
    :param e: RSA public exponent
    :param parallel: how many parallel processes to run, best effects with n-1 or n-2, where n is number of cores you have
    :param major_chunk_size: size of the data split chunk
    :param minor_chunk_size: size of single multiplication chunk
    :return: attack result, most likely RSA plaintext if there was enough data
    """
    import gmpy2
    print("With this setup you can recover RSA message only if length was < %f of the average modulus size" % (len(residue_and_moduli) / (e * 1.0)))
    if major_chunk_size % parallel != 0 or minor_chunk_size % parallel != 0:
        print("Keep in mind that it's better to choose chunk size as multiples of parallel processes count")
    crt = solve_crt(residue_and_moduli, parallel, major_chunk_size, minor_chunk_size)
    solution, _ = gmpy2.iroot(crt, e)
    return solution


def solve_crt(residue_and_moduli, parallel=6, major_chunk_size=1000, minor_chunk_size=100):
    residues, moduli = zip(*residue_and_moduli)
    print("Calculate composite modulus N")
    N = multiply(moduli, parallel)
    chunks = len(residues) // major_chunk_size
    print("Number of major chunks", chunks + 1)
    solution = 0
    for i in range(chunks + 1):
        print("Calculating major chunk", i + 1)
        print("Calculating Nx = n//N")
        moduli_slice = moduli[i * major_chunk_size:(i + 1) * major_chunk_size]
        residue_slice = residues[i * major_chunk_size:(i + 1) * major_chunk_size]
        Nxs = calculate_nxs(N, moduli_slice, parallel)
        print("Calculating d = modinv(nx,n)")
        ds = calculate_modinvs(Nxs, moduli_slice, parallel)
        print("Calculating mult = nx * residue * d, and adding them up")
        solution = (solution + calculate_mults_and_add(Nxs, ds, residue_slice, N, minor_chunk_size, parallel)) % N
        del Nxs
        del ds
        del moduli_slice
        del residue_slice
    return solution


def worker_multiply(data):
    return functools.reduce(gmpy2.mul, data, 1)


def multiply(values, parallel):
    partials = brute(worker_multiply, chunk_with_remainder(values, 100), processes=parallel)
    return functools.reduce(gmpy2.mul, partials, 1)


def worker_mults(data):
    r, Nx, d = data
    return r * Nx * d


def mults_data_gen_slice(residues, Nxs, ds, start, stop):
    all = len(residues)
    for i in range(start, stop):
        if not i < all:
            return
        yield residues[i], Nxs[i], ds[i]


def calculate_mults_and_add_partial(data, N, parallel):
    print("Calculating minor chunk")
    return functools.reduce(gmpy2.add, brute(worker_mults, data, processes=parallel), 1) % N


def calculate_mults_and_add(Nxs, ds, residues, N, minor_chunk_size, parallel):
    chunks = len(residues) // minor_chunk_size
    print("Minor chunks number", chunks + 1)
    result = 0
    for start in range(chunks + 1):
        data = mults_data_gen_slice(residues, Nxs, ds, start * minor_chunk_size, (start + 1) * minor_chunk_size)
        partial = calculate_mults_and_add_partial(data, N, parallel)
        result = (result + partial) % N
        del data
    return result


def worker_nxs(data):
    N, n = data
    return N // n


def data_gen(N, values):
    for n in values:
        yield (N, n)


def calculate_nxs(N, moduli, parallel):
    return brute(worker_nxs, data_gen(N, moduli), parallel)


def worker_mod(data):
    nx, n = data
    return gmpy2.invert(nx, n)


def calculate_modinvs(Nxs, moduli, parallel):
    return brute(worker_mod, zip(Nxs, moduli), processes=parallel)


def sanity_test():
    x = bytes_to_long("alamakota")
    e = gmpy2.next_prime(50)
    inputs = []
    for _ in range(e - 40):
        print(_)
        p = gmpy2.next_prime(getrandbits(1024))
        q = gmpy2.next_prime(getrandbits(1024))
        n = p * q
        inputs.append((pow(x, e, n), n))
    result = hastad_attack_parallel(inputs, e)
    print(result)
    print(long_to_bytes(result))


if __name__ == '__main__':
    freeze_support()
    sanity_test()
