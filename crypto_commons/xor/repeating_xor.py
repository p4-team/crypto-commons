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
        print(">")
        potential_contents = raw_input()
        ct_len = len(ciphertexts[0])
        if len(potential_contents) > ct_len:
            print("Can't break more than a single block at a time! Taking prefix '" + potential_contents[:ct_len] + "'")
        for index, xored_ciphertext in enumerate(xored):
            missing_bytes = len(xored_ciphertext) - len(potential_contents)
            for start_position in set(range(missing_bytes)+[0]):
                uncovered_content = xor_string(potential_contents, xored_ciphertext[start_position:start_position + len(potential_contents)])
                print(uncovered_content,
                      'key=(' + format_potential_key(ciphertexts, index, missing_bytes, start_position, uncovered_content)
                      + ') or ' +
                      'key=(' + format_potential_key(ciphertexts, index + 1, missing_bytes, start_position, uncovered_content)
                      )


def format_potential_key(ciphertexts, index, missing_bytes, start_position, uncovered_content):
    partial_input = ciphertexts[index][start_position:start_position + len(uncovered_content)]
    return "?" * start_position + xor_string(uncovered_content, partial_input).encode("hex") + "?" * (missing_bytes - start_position)
