"""
Client class
"""


import socket
import select
import errno
import sys


HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234


my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header + username)

while True:
    msg = input(f"{my_username} > ")
    if msg:
        msg = msg.encode("utf-8") 
        msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(msg_header + msg)
    
    try:
        while True:
            # receive things
            username_header = client_socket.recv(HEADER_LENGTH)
            if len(username_header) == 0:
                print("connection closed by the server")
                sys.exit()

            username_length = int(username_header.decode("utf-8").strip())
            username = client_socket.recv(username_length).decode("utf-8")

            msg_header = client_socket.recv(HEADER_LENGTH)
            msg_length = int(msg_header.decode("utf-8").strip())
            msg = client_socket.recv(msg_length).decode("utf-8")

            print(f"{username} > {msg}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno. EWOULDBLOCK:
            print("Reading error", str(e))
            sys.exit()
        continue

    except Exception as e:
        print("General error", str(e))
        sys.exit()