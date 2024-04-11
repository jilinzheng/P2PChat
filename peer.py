"""
Peer class, capable of both client and server functionality, enabling P2P networking
"""


import socket
import select
import threading


class Peer:
    """ Peer class, capabale of both client and server functionality """

    # ip and port of central server for user discovery
    CENTRAL_SERVER_IP = "127.0.0.1"
    CENTRAL_SERVER_PORT = "12345"

    def __init__(self,
                 header_len=10,
                 username="new_user"):

        """
        Initialize header length and usernmae for messages and connections, respectively,
        as well as other to-be-initialized attributes
        
        params:
        :header_len: length of the header in bytes; a value representing how many bytes to read/send from the server/client
        :username: the username for the client socket opened (conn_socket)
        """
        self.header_len = header_len
        self.username = username
        self.serv_ip = None
        self.serv_port = None
        self.serv_socket = None
        self.conn_ip = None
        self.conn_port = None
        self.conn_socket = None
        self.session_active = False
        # for multi-client capabilities
        #self.socket_list = []
        #self.clients = {}
    
    def init_server(self, serv_ip, serv_port):
        """
        Initialize a server with an ip and port that accepts other peer connections

        params:
        :serv_ip: ip of your peer server being served
        :serv_port: port of your peer server being served
        """
        self.serv_ip = serv_ip
        self.serv_port = serv_port
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind((self.serv_ip, self.serv_port))
        self.serv_socket.listen()
        self.socket_list.append(self.serv_socket)

    def init_client(self, conn_ip, conn_port):
        """
        Initialize a client that connects to another peer
        
        params:
        :conn_ip: ip of client that connection is desired with
        :conn_port: port of client that connection is desired with
        """
        self.conn_ip = conn_ip
        self.conn_port = conn_port
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_socket.connect((self.conn_ip, self.conn_port))
        self.conn_socket.setblocking(False)

    def send_msg(self, msg):
        """
        Sends a message via a previously initialized client to its connection
        
        params:
        :msg: desired message to be sent
        """
        print(f"MESSAGE TO BE SENT: {msg}")
        msg = msg.encode("utf-8")
        msg_header = f"{len(msg):<{self.header_len}}".encode("utf-8")
        self.conn_socket.send(msg_header+msg)

    def recv_msg(self):
        """
        Handles messages sent to the initiated server
        """
        conn, addr = self.serv_socket.accept()
        print(f"NEW CONNECTION ACCEPTED FROM {addr[0]}:{addr[1]}, with username")

        while self.session_active:
            #read_sockets, _, _, = select.select(self.socket_list)
            

    def start_session(self):
        """
        Begins a session via the initiated client, with threaded subroutines
        """
        self.session_active = True
        recv_thread = threading.Thread(target=self.recv_msg, args=[self]) 
        recv_thread.start()

        # send the username over to the client
        username = self.username.encode("utf-8")
        username_header = f"{len("UNAME"+self.username):<{self.header_len}}".encode("utf-8")
        self.conn_socket.send(username_header+username)

        while self.session_active:
            msg = input(f"{self.username} > ")
            if msg == ':q!': # inspired by vim, exit the session
                self.session_active = False
                break

            send_thread = threading.Thread(target=self.send_msg, args=[self, msg])
            send_thread.start()
            send_thread.join() # block until the current message has finished sending

        recv_thread.join()
        print("SUCCESSFULLY EXITED SESSION")
