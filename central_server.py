"""
Central server, provides user discovery and database management routines
"""


import socket
import select


# CONSTANTS
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 13530


# GLOBAL VARS
connected_sockets = []  # list of all connected sockets, including this socket
connected_users = {}    # list of connected users, populated as connections are recieved


# INITIALIZE CENTRAL SERVER SOCKET
central_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
central_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
central_server.bind((IP, PORT))
central_server.listen()
connected_sockets.append(central_server)


# RUN CENTRAL SERVER INDEFINITELY
while True:
    print("Central sever is standing by for connections...")
    ready_sockets, _, excepted_sockets = select.select(connected_sockets)     # get all of the ready and excepted sockets, note that these are ready-to-be-READ sockets

    for s in ready_sockets:
        if s is central_server:
            user_socket, user_addr = central_server.accept()

            """ save the user into connected users"""
        
        else: # the socket is an user socket
            """ handle user requests for discovery and starting sessions with other users """

    for e in excepted_sockets:
        connected_sockets.remove(e)
        del connected_users[e]
