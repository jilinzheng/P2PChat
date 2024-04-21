"""
Central server, provides user discovery and database management routines
"""


import socket
import select
import json


# CONSTANTS
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 50000


# INITIALIZE CENTRAL SERVER SOCKET
central_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
central_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
central_server.bind((IP, PORT))
central_server.listen()

connected_sockets = []  # list of all connected sockets, including this socket
connected_clients = {}  # dict of connected users + metadata, populated as connections are recieved
connected_sockets.append(central_server)

def receive_msg(client_socket, client_addr):
    global connected_sockets, connected_clients
   # get the msg_header and use it to receive/read appropriate amount of bytes
    msg_header = client_socket.recv(HEADER_LENGTH)
    if not msg_header:
        return
    msg_length = int(msg_header.decode("utf-8").strip())
    msg = (client_socket.recv(msg_length)).decode("utf-8")
    #print(f"MSG RECEIVED: {msg}")

    # handle the client's first message upon connection (entering username)
    if msg[0:8] == "USERNAME":
        username = msg[8:]
        print(f"Successfully connected user '{username}' at address '{client_addr}'")
        serv_port_header = client_socket.recv(HEADER_LENGTH)
        if not serv_port_header:
            return
        serv_port_length = int(serv_port_header.decode("utf-8").strip())
        serv_port = int((client_socket.recv(serv_port_length)).decode("utf-8"))
        connected_clients[client_socket] = {'username':username, 'addr':("127.0.0.1", serv_port)}

    # return the list of clients currently registered in the central server
    elif msg[0:9] == "get_users":
        clients_list = []
        for client in connected_clients.values():
            clients_list.append({client['username'], client['addr']})
            #print(client)
            #print(type(client))
        clients_list = (json.dumps(clients_list, default=list)).encode("utf-8")
        clients_list_header = f"{len(clients_list):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(clients_list_header+clients_list)
        print("CLIENTS LIST SENT!")

    # close the client connection
    elif msg[0:10] == "close_conn":
        connected_sockets.remove(client_socket)
        del connected_clients[client_socket]
        client_socket.close()
        print("DISCONNECTED USER")

    # otherwise just reiterate avilable central-server commands
    else:
        msg = """This is a peer-to-peer network.
You are currently connected to the central network. The following commands are available (simply send them as messages):
get_users: discover available users/clients (registered in this central server)
close_conn: close the current connection to the central server"""
        msg = msg.encode("utf-8")
        msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(msg_header+msg)


# RUN CENTRAL SERVER INDEFINITELY
while True:
    #print("Central server is standing by for connections...")
    # get all of the ready and excepted sockets, note that these are ready-to-be-READ sockets
    ready_sockets, _, excepted_sockets = select.select(connected_sockets, [], [])

    for s in ready_sockets:
        if s is central_server:
            client_socket, client_addr = central_server.accept()
            if client_socket not in connected_sockets:
                connected_sockets.append(client_socket)
            msg = receive_msg(client_socket, client_addr)
        else: # all other client sockets
            msg = receive_msg(s, None)
