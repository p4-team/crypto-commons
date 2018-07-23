import re
import string
import sys

from crypto_commons.generic import chunk, xor_hex, chunk_with_remainder


def brute_ecb_suffix(encrypt_function, block_size=16, expected_suffix_len=32, pad_char='A'):
    suffix = ""
    recovery_block = expected_suffix_len / block_size - 1
    for i in range(expected_suffix_len - len(suffix) - 1, -1, -1):
        data = pad_char * i
        correct = chunk(encrypt_function(data), block_size)[recovery_block]
        for character in range(256):
            c = chr(character)
            test = data + suffix + c
            try:
                encrypted = chunk(encrypt_function(test), block_size)[recovery_block]
                if correct == encrypted:
                    suffix += c
                    print('FOUND', expected_suffix_len - i, c)
                    break
            except:
                pass
    return suffix


def create_byte_search_block(size_block, i, pos, l):
    hex_char = chr(pos).encode("hex")
    return "00" * (size_block - (i + 1)) + hex_char + ''.join(l)


def create_block_padding(size_block, i):
    l = [chr(i + 1).encode("hex") for _t in range(0, i + 1)]
    return "00" * (size_block - (i + 1)) + ''.join(l)


def oracle_padding_recovery(ciphertext, oracle_fun, size_block=16, search_charset=string.printable):
    """
    Orale padding attack based on https://github.com/mpgn/Padding-oracle-attack/blob/master/exploit.py
    :param ciphertext: 
    :param oracle_fun: 
    :param size_block: 
    :param search_charset: 
    :return: 
    """
    ciphertext = ciphertext.upper()
    result = []
    len_block = size_block * 2
    cipher_block = chunk_with_remainder(ciphertext, len_block)
    if len(cipher_block) == 1:
        print("[-] Abort, there is only one block")
        return
    for block in reversed(range(1, len(cipher_block))):
        if len(cipher_block[block]) != len_block:
            print("[-] Abort, block length doesn't match the size_block")
            break
        recovered_block = recover_block(block, cipher_block, oracle_fun, size_block, search_charset)
        result.insert(0, recovered_block)
        print("[+] Decrypted current value (ASCII):", "".join(result).decode("hex"))
    print()
    hex_result = ''.join(result).upper()
    print("[+] Decrypted value (HEX):", hex_result)
    padding_length = int(hex_result[len(hex_result) - 2:len(hex_result)], 16)
    print("[+] Decrypted value (ASCII):", hex_result[0:-(padding_length * 2)].decode("hex"))


def recover_block(block, cipher_block, oracle_fun, size_block, search_charset):
    valid_value = []
    print("[+] Search value of block:", block, "\n")
    for i in range(0, size_block):
        found = False
        for index, ct_pos in enumerate((map(ord, search_charset))):
            if ct_pos != i + 1 or (
                    len(valid_value) > 0 and int(valid_value[len(valid_value) - 1], 16) == ct_pos):
                bk = create_byte_search_block(size_block, i, ct_pos, valid_value)
                bp = cipher_block[block - 1]
                bc = create_block_padding(size_block, i)
                tmp = xor_hex(bk, bp)
                cb = xor_hex(tmp, bc).upper()
                up_cipher = "".join(cipher_block[:block - 1]) + cb + cipher_block[block]
                response = oracle_fun(up_cipher)
                exe = re.findall('..', cb)
                discover = ''.join(exe[size_block - i:size_block])
                current = ''.join(exe[size_block - i - 1:size_block - i])
                find_me = ''.join(exe[:-i - 1])
                sys.stdout.write(
                    "\r[+] Test [Byte (0x%02x) %03i/%03i - Block %d ]: \033[31m%s\033[33m%s\033[36m%s\033[0m" % (
                        ct_pos, index, len(search_charset), block, find_me, current, discover))
                sys.stdout.flush()
                if response:
                    found = True
                    value = re.findall('..', bk)
                    valid_value.insert(0, value[size_block - (i + 1)])
                    print()
                    print("[+] Block M_Byte : %s" % bk)
                    print("[+] Block C_{i-1}: %s" % bp)
                    print("[+] Block Padding: %s" % bc)
                    print()
                    bytes_found = ''.join(valid_value)
                    print('\033[36m' + '\033[1m' + "[+]" + '\033[0m' + " Found", i + 1, "bytes :", bytes_found)
                    print('\033[36m' + '\033[1m' + "[+]" + '\033[0m' + " Found", i + 1, "bytes (ascii) :", bytes_found.decode("hex"))
                    print()
                    break
        if not found:
            print("\n[-] Error, decryption failed for byte %d" % i)
            valid_value.insert(0, '3f')
            print()
            bytes_found = ''.join(valid_value)
            print('\033[36m' + '\033[1m' + "[+]" + '\033[0m' + " Found", i + 1, "bytes :", bytes_found)
            print('\033[36m' + '\033[1m' + "[+]" + '\033[0m' + " Found", i + 1, "bytes :", bytes_found.decode("hex"))
            print()
    return ''.join(valid_value)


def set_byte_cbc(ct_bytes, pt_bytes, byte_number, new_value, block_size=16):
    decrypted_byte = pt_bytes[byte_number]
    bytes_list = list(ct_bytes)
    bytes_list[byte_number - block_size] = chr(
        ord(ct_bytes[byte_number - block_size]) ^ ord(decrypted_byte) ^ ord(new_value))
    return "".join(bytes_list)


def set_cbc_payload_for_block(ct, pt, payload, block_number, block_size=16):
    assert len(payload) <= block_size, "Payload can't be longer than a single block size!"
    new_ct = ct
    for i, c in enumerate(payload):
        new_ct = set_byte_cbc(new_ct, pt, block_number * block_size + i, c)
    return new_ct
