import string

from crypto_commons.generic import chunk


def brute_aes_suffix(encrypt, known_suffix="", expected_suffix_len=64, prefix=""):
    suffix = known_suffix
    recovery_block = expected_suffix_len / 32 + 1
    for i in range(expected_suffix_len - len(suffix), 0, -1):
        data = prefix + 'A' * i
        correct = chunk(encrypt(data), 32)[recovery_block]
        for c in '{' + "}" + "_" + string.letters + string.digits:
            test = data + suffix + c
            try:
                encrypted = chunk(encrypt(test), 32)[3]
                if correct == encrypted:
                    suffix += c
                    print('FOUND', expected_suffix_len - i, c)
                    if c == "}":
                        print(suffix)
                        return suffix
                    break
            except:
                pass
    return suffix
