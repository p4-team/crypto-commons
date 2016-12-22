from crypto_commons.generic import long_to_bytes


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
    flag_count = n_count = 1
    data_lower_bound = 0
    data_upper_bound = upper_bound
    ciphertext = encrypted_data
    mult = 1
    while data_upper_bound > data_lower_bound + 1:
        ciphertext = multiplicator(ciphertext)
        flag_count *= 2
        n_count = n_count * 2 - 1
        print("upper = %d" % data_upper_bound)
        print("upper flag = %s" % long_to_bytes(data_upper_bound))
        print("lower = %d" % data_lower_bound)
        print("lower flag = %s" % long_to_bytes(data_lower_bound))
        print("bit = %d" % mult)
        mult += 1
        if oracle_fun(ciphertext) == 0:
            data_upper_bound = upper_bound * n_count / flag_count
        else:
            data_lower_bound = upper_bound * n_count / flag_count
            n_count += 1
    return data_upper_bound
