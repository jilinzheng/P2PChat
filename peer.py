"""
Peer class, capable of both client and server functionality, enabling P2P networking
"""


import socket
import select


class Peer:
    """ Peer class, capabale of both client and server functionality """
    def __init__(self,
                 header_length=10,
                 serv_ip="127.0.0.1",
                 serv_port="12345",
                 conn_ip="127.0.0.1",
                 conn_port="54321"):
        """ Initialize peer sockets for both serving and connecting """
        self.header_length = header_length
        self.serv_ip = serv_ip
        self.serv_port = serv_port
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind((self.serv_ip, self.serv_port))
        self.serv_socket.listen()
        self.conn_ip = conn_ip
        self.conn_port = conn_port
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_socket.connect((self.conn_ip, self.conn_port))
        self.conn_socket.setblocking(False)

    def start():
        pass
