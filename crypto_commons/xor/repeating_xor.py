from crypto_commons.generic import xor_string, is_printable


def repeating_key_xor(ciphertexts, printable=False):
    """
    Run interactive session of repeating key xor breaking.
    :param ciphertexts: list of ciphertexts xored with the same repeating key
    """
    import itertools
    xored_ciphertexts = [xor_string(first, second) for (first, second) in itertools.product(ciphertexts, repeat=2)]
    interactive_hack(xored_ciphertexts, ciphertexts, printable)


def interactive_hack(xored, ciphertexts, printable=False):
    from builtins import input, range
    while True:
        potential_plaintext_contents = input(">")
        ciphertext_len = len(ciphertexts[0])
        if len(potential_plaintext_contents) > ciphertext_len:
            err = "Can't break more than a single block at a time! Taking prefix '%s'"
            print(err % potential_plaintext_contents[:ciphertext_len])

        max_missing_bytes = max(map(len, xored)) - len(potential_plaintext_contents)
        for start_position in set(range(max_missing_bytes)).union({0}):
            for index, xored_ciphertext in enumerate(xored):
                number_of_ciphertexts = len(ciphertexts)
                first_xored_ct_index = index / number_of_ciphertexts
                second_xored_ct_index = index % number_of_ciphertexts
                if len(xored_ciphertext) > start_position and first_xored_ct_index != second_xored_ct_index:
                    uncovered_content = xor_string(potential_plaintext_contents,
                                                   xored_ciphertext[start_position:start_position + len(potential_plaintext_contents)])
                    if (printable and is_printable(uncovered_content)) or not printable:
                        print('in ' + str(first_xored_ct_index), 'ct ' + str(second_xored_ct_index), 'offset ' + str(start_position), uncovered_content,
                              'key=(' + format_potential_key(ciphertexts, second_xored_ct_index, max_missing_bytes, start_position, uncovered_content) + ')')


def format_potential_key(ciphertexts, second_xored_ct_index, missing_bytes, start_position, uncovered_content):
    return "?" * start_position + xor_string(uncovered_content,
                                             ciphertexts[second_xored_ct_index][start_position:start_position + len(uncovered_content)]).encode(
        "hex") + "?" * (missing_bytes - start_position)
