from crypto_commons.brute.brute import brute
from crypto_commons.generic import long_to_bytes


def lsb_oracle_distributed(encrypted_data, multiplicator, upper_bound, oracle_fun, processes=8):
    """
    LSB oracle attack implementation, recovering bits in parallel.
    CPython has issues with pickling functions, so use PyPy instead in case of trouble.
    Keep in mind the progress will be visible only once all bits are collected!
    To see progress right away use the serial version.
    :param encrypted_data: initial encrypted data
    :param multiplicator: function to multiply ciphertext in a way such that plaintext after decoding is multiplied by 2
    :param upper_bound: upper bound for the plaintext, most likely modulus
    :param oracle_fun: lsb oracle function returning LSB of plaintext for given ciphertext
    :param processes: number of parallel processes
    :return: plaintext value
    """

    def distributed_bits_collector(encrypted_data, multiplicator, upper_bound, oracle_fun, processes):
        def worker(data):
            index, ct = data
            bit = oracle_fun(ct)
            print("Recovered bit %d -> %d" % (index, bit))
            return index, bit

        ciphertext = encrypted_data
        data_set = []
        for i in range(len(bin(upper_bound)) - 2):
            ciphertext = multiplicator(ciphertext)
            data_set.append((i, ciphertext))
        results = brute(worker, data_set, processes)
        sorted(results, key=lambda x: x[0])
        return [bit for index, bit in results]

    bits = distributed_bits_collector(encrypted_data, multiplicator, upper_bound, oracle_fun, processes)
    return lsb_oracle_from_bits(upper_bound, iter(bits))


def lsb_oracle(encrypted_data, multiplicator, upper_bound, oracle_fun):
    """
    LSB oracle attack implementation.
    This one is actually working for all bytes, taking into account +-1 errors.
    :param encrypted_data: initial encrypted data
    :param multiplicator: function to multiply ciphertext in a way such that plaintext after decoding is multiplied by 2
    :param upper_bound: upper bound for the plaintext, most likely modulus
    :param oracle_fun: lsb oracle function returning LSB of plaintext for given ciphertext
    :return: plaintext value
    """

    def bits_provider():
        ciphertext = encrypted_data
        while True:
            ciphertext = multiplicator(ciphertext)
            yield oracle_fun(ciphertext)

    return lsb_oracle_from_bits(upper_bound, bits_provider())


def lsb_oracle_from_bits(upper_bound, bits):
    """
    Use binary search to recover plaintext from LSB bits.
    :param upper_bound: upper bound for the plaintext, most likely modulus
    :param bits: list of LSB bits
    :return: recovered plaintext
    """
    flag_count = n_count = 1
    data_lower_bound = 0
    data_upper_bound = upper_bound
    mult = 1
    for bit in bits:
        flag_count *= 2
        n_count = n_count * 2 - 1
        print("bit value = %d" % bit)
        print("upper = %d" % data_upper_bound)
        print("upper flag = %s" % long_to_bytes(data_upper_bound))
        print("lower = %d" % data_lower_bound)
        print("lower flag = %s" % long_to_bytes(data_lower_bound))
        print("bit = %d" % mult)
        print("flag_cnt = %d" % flag_count)
        print("n_cnt = %d" % n_count)
        mult += 1
        if bit == 0:
            data_upper_bound = upper_bound * n_count / flag_count
        else:
            data_lower_bound = upper_bound * n_count / flag_count
            n_count += 1
        if data_upper_bound <= data_lower_bound + 1:
            break
    return data_upper_bound
