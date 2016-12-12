import socket


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
    return all_data


def send(s, payload):
    s.sendall(payload + "\n")
