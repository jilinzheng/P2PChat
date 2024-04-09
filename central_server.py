"""
Central server, provides user discovery and database management routines
"""


import socket
import select
import json


# CONSTANTS
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 13530


# GLOBAL VARS
connected_sockets = []  # list of all connected sockets, including this socket
connected_clients = {}  # dict of connected users + metadata, populated as connections are recieved


# INITIALIZE CENTRAL SERVER SOCKET
central_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
central_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
central_server.bind((IP, PORT))
central_server.listen()
connected_sockets.append(central_server)


def receive_msg(client_socket, client_addr):
   # get the msg_header and use it to receive/read appropriate amount of bytes
    msg_header = client_socket.recv(HEADER_LENGTH)
    msg_length = int(msg_header.decode("utf-8").strip())
    msg = (client_socket.recv(msg_length)).decode("utf-8")

    # handle the client's first message upon connection (entering username)
    if msg[0:10] == "username:":
        username = msg.split()[1]
        connected_clients[client_socket] = {'username':username, 'addr':client_addr}
        return f"Successfully connected user '{username}' at address '{client_addr}'"
    # return the list of clients currently registered in the central server
    elif msg[0:10] == "get_users":
        client_socket.send(json.dumps(connected_clients)).encode("utf-8")
        return None
    elif msg[0:11] == "close_conn":
        connected_sockets.remove(client_socket)
        del connected_clients
        client_socket.close()
        return f"Successfully disconnected user '{username}' at address '{client_addr}'"
    # otherwise just reiterate avilable central-server commands
    else:
        return """
        This is a peer-to-peer network. You are currently connected to the central network. The following commands are available (simply send them as messages):
        get_users: discover available users/clients (registered in this central server)
        close_conn: close the current connection to the central server
        """


# RUN CENTRAL SERVER INDEFINITELY
while True:
    print("Central server is standing by for connections...")
    ready_sockets, _, excepted_sockets = select.select(connected_sockets)     # get all of the ready and excepted sockets, note that these are ready-to-be-READ sockets

    for s in ready_sockets:
        if s is central_server:
            client_socket, client_addr = central_server.accept()
            if client_socket not in connected_sockets:
                connected_sockets.append(client_socket)
            msg = receive_msg(client_socket, client_addr)
            if msg is not None:
                print(msg)
        else:       # the socket is a client socket
            pass    # at this point all the functionality of the central server is within the receive_msg helper function

    for e in excepted_sockets:
        connected_sockets.remove(e)
        del connected_clients[e]
