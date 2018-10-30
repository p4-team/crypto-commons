import re
import socket
import telnetlib


def nc(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def receive_until(s, delimiters, break_on_empty=False):
    all_data = ""
    data = s.recv(1)
    while data not in delimiters:
        all_data += data
        data = s.recv(1)
        if data == '' and break_on_empty:
            return all_data
    return all_data + data


def receive_until_match(s, regex, timeout=None, limit=-1, break_on_empty=False):
    """
    Receive data from socket until regular expression is matching
    :param s: socket
    :param regex: regex to match
    :param timeout: read timeout, None for no timeout
    :param limit: data read attempts limit
    :return: read data
    """
    s.settimeout(timeout)
    all_data = ""
    i = 0
    try:
        while re.search(regex, all_data) is None:
            new_char = s.recv(1)
            all_data += new_char
            if (limit != -1 and i > limit) or (new_char == '' and break_on_empty):
                break
            i += 1
    except Exception as e:
        print('error', e)
        print(all_data)
    s.settimeout(None)
    return all_data


def send(s, payload):
    s.sendall(payload + "\n")


def interactive(s):
    t = telnetlib.Telnet()
    t.sock = s
    t.interact()
