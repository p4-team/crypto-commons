import socket
import telnetlib
import re


def nc(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def receive_until(s, delimiters):
    all_data = ""
    data = s.recv(1)
    while data not in delimiters:
        all_data += data
        data = s.recv(1)
    return all_data + data


def receive_until_match(s, regex, timeout=1.0, limit=-1):
    """
    Receive data from socket until regular expression is matching
    :param s: socket
    :param regex: regex to match
    :param timeout: read timeout
    :param limit: data read attempts limit
    :return: read data
    """
    s.settimeout(timeout)
    all_data = ""
    i = 0
    try:
        while re.search(regex, all_data) is None:
            new_char = s.recv(1)
            if (limit != -1 and i > limit) or new_char == '':
                break
            all_data += new_char
            i += 1
    except:
        pass
    return all_data


def send(s, payload):
    s.sendall(payload + "\n")


def interactive(s):
    t = telnetlib.Telnet()
    t.sock = s
    t.interact()
