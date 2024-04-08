"""
Server class.
"""


import socket
import select


HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()


sockets_list = [server_socket,]
clients = {}


def receive_msg(client_socket):
    """ Receive a message from a client socket """
    try:
        msg_header = client_socket.recv(HEADER_LENGTH)
        if len(msg_header) == 0:
            return False

        msg_length = int(msg_header.decode("utf-8").strip())
        return {"header": msg_header, "data": client_socket.recv(msg_length)}

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_msg(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user["data"].decode("utf-8")}")
        else:
            msg = receive_msg(notified_socket)

            if msg is False:
                print(f"Closed connection from {clients[notified_socket]["data"].decode("utf-8")}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f"Received message from {user["data"].decode("utf-8")}: {msg["data"].decode("utf-8")}")
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user["header"] + user["data"] + msg["header"] + msg["data"])
    
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
