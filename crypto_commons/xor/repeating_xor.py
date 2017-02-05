from crypto_commons.generic import xor_string


def repeating_key_xor(ciphertexts):
    """
    Run interactive session of repeating key xor breaking.
    :param ciphertexts: list of ciphertexts xored with the same repeating key
    """
    xored = [xor_string(ciphertexts[0], d) for d in ciphertexts[1:]]
    interactive_hack(xored, ciphertexts)


def interactive_hack(xored, ciphertexts):
    while True:
        print ">",
        potential_contents = raw_input()
        for index, xored_ciphertext in enumerate(xored):
            uncovered_content = xor_string(potential_contents * (len(xored_ciphertext) / len(potential_contents)),
                                           xored_ciphertext)
            print(uncovered_content,
                  'key=(' + xor_string(uncovered_content, ciphertexts[index]) + ') or ' + 'key=(' + xor_string(
                      uncovered_content, ciphertexts[index + 1]))
