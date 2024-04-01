"""
Tutorial server.py
"""


import socket
import time


HEADER_SIZE = 10


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1227))
s.listen(5)


while True:
    client_socket, address = s.accept()
    print(f'Connect from {address} has been established!')

    msg = 'Welcome to the server!'
    msg = f'{len(msg):<{HEADER_SIZE}}' + msg
    client_socket.send(msg.encode('utf-8'))

    while True:
        time.sleep(3)
        msg = f'The time is {time.time()}!'
        msg = f'{len(msg):<{HEADER_SIZE}}' + msg
        client_socket.send(msg.encode('utf-8'))
