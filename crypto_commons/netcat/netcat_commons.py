import socket

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


def receive_until_match(s, regex):
    s.settimeout(5.0)
    all_data = ""
    try:
        all_data += s.recv(1)
        while re.search(regex, all_data) is None:
            all_data += s.recv(1)
        return all_data
    except:
        return all_data


def send(s, payload):
    s.sendall(payload + "\n")
