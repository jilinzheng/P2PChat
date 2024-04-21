"""
Peer class, capable of both client and server functionality, enabling P2P networking
"""


from multiprocessing import Value
import socket
import threading
import sqlite3


class Peer:
    """ Peer class, capabale of both client and server functionality """

    # ip and port of central server for user discovery
    CENTRAL_SERVER_IP = "127.0.0.1"
    CENTRAL_SERVER_PORT = 50000

    def __init__(self, header_len, username):

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
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_ip = None
        self.conn_port = None
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock() # for locking prints to stdout
        self.db = None
        self.cursor = None

    def init_server(self, serv_ip, serv_port):
        """
        Initialize a server with an ip and port that accepts other peer connections

        params:
        :serv_ip: ip of your peer server being served
        :serv_port: port of your peer server being served
        """
        self.serv_ip = serv_ip
        self.serv_port = serv_port
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind((self.serv_ip, self.serv_port))
        self.serv_socket.listen()
        print("Server successfully initialized!")

    def init_client(self, conn_ip, conn_port):
        """
        Initialize a client that connects to another peer

        params:
        :conn_ip: ip of client that connection is desired with
        :conn_port: port of client that connection is desired with
        """
        self.conn_ip = conn_ip
        self.conn_port = conn_port
        self.conn_socket.connect((self.conn_ip, self.conn_port))
        self.conn_socket.setblocking(True)
        print("Client successfully initialized!")

    def init_db(self):
        self.db = sqlite3.connect(f"{self.username}.db", check_same_thread=False)
        self.cursor = self.db.cursor()

        table = """
            CREATE TABLE IF NOT EXISTS recv_msgs (
            user VARCHAR(255) NOT NULL,
            msg TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        self.cursor.execute(table)
        print("SQLITE DATABASE+TABLE SUCCESSFULLY CREATED/CONNECTED")

    def send_msg(self, msg):
        """
        Sends a message via a previously initialized client to its connection

        params:
        :msg: desired message to be sent
        """
        msg = msg.encode("utf-8")
        msg_header = f"{len(msg):<{self.header_len}}".encode("utf-8")
        self.conn_socket.send(msg_header+msg)

    def recv_msg(self):
        """
        Handles messages sent to the initiated server
        """
        self.lock.acquire()
        conn, addr = self.serv_socket.accept()
        print(f"NEW CONNECTION ACCEPTED FROM {addr[0]}:{addr[1]}", flush=True)
        self.lock.release()

        # first received message should always be username
        msg_header = conn.recv(self.header_len)
        msg_len = int(msg_header.decode("utf-8").strip())
        msg = (conn.recv(msg_len)).decode("utf-8")
        conn_username = ""
        if msg[0:8] == "USERNAME":
            self.lock.acquire()
            print(f"USERNAME RECEIVED: {msg[8:]}", flush=True)
            self.lock.release()
            conn_username = msg[8:]
            # input sanitization
            conn_username = conn_username.replace('"', "")
            conn_username = conn_username.replace("'", "")
            conn_username = conn_username.replace(";", "")

        while self.session_active:
            try:
                msg_header = conn.recv(self.header_len)
                msg_len = int(msg_header.decode("utf-8").strip())
                msg = (conn.recv(msg_len)).decode("utf-8")
                print(conn_username + " > " + msg, flush=True)
                # input sanitization
                msg = msg.replace('"', "")
                msg = msg.replace("'", "")
                msg = msg.replace(";", "")
                table_entry = f"""
                    INSERT INTO recv_msgs (user, msg)
                    VALUES (\"{conn_username}\", \"{msg}\");
                    """
                self.cursor.execute(table_entry)
                self.db.commit()
            except ValueError:
                continue

    def cs_recv(self):
        while self.session_active:
            try:
                msg_header = self.conn_socket.recv(self.header_len)
                msg_len = int(msg_header.decode("utf-8").strip())
                msg = (self.conn_socket.recv(msg_len)).decode("utf-8")
                print(msg)
            except OSError:
                return
            except ValueError:
                return

    def start_session(self):
        """
        Begins a session via the initiated client, with threaded send/receive subroutines
        """
        self.session_active = True
        recv_thread = threading.Thread(target=self.recv_msg, daemon=True)
        recv_thread.start()

        # send the username over to the client
        username = ("USERNAME" + self.username).encode("utf-8")
        username_header = f"{len("USERNAME"+self.username):<{self.header_len}}".encode("utf-8")
        self.conn_socket.send(username_header+username)
         
        if self.conn_port == 50000:
            cs_recv_thread = threading.Thread(target=self.cs_recv, daemon=True)
            cs_recv_thread.start()
            serv_port = (str(self.serv_port)).encode("utf-8")
            serv_port_header = f"{len(serv_port):<{self.header_len}}".encode("utf-8")
            self.conn_socket.send(serv_port_header+serv_port)
       
        while self.session_active:
            choice = input()
            if choice == "i":
                msg = input(f"{self.username} (me) > ")
                send_thread = threading.Thread(target=self.send_msg, args=[msg])
                send_thread.start()
                send_thread.join() # block until the current message has finished sending
            elif choice == ':q!': #inpsired by vim, quit the session
                print("EXITING SESSION")
                self.session_active = False
                self.conn_socket.close()

        recv_thread.join(timeout=2)
        self.conn_socket.close()
        print("SUCCESSFULLY EXITED SESSION")

    def show_saved_msgs(self):
        entries = self.cursor.execute("""SELECT * FROM recv_msgs""")
        for row in entries:
            print(row)


if __name__ == "__main__":
    username = input("Enter your username: ")
    peer = Peer(header_len=10, username=username)
    serv_port = int(input("Enter your server port, i.e. what port others will connect to you with: "))
    peer.init_server(serv_ip="127.0.0.1", serv_port=serv_port) # serve on localhost
    print(f"Your peer server has been initialized! Clients can connect to you with '127.0.0.1:{serv_port}'!")
    peer.init_db()

    while True:
        choice = input("""What would you like to do?
Enter '0' to connect to the Central Server.
Enter '1' to connect to another user.
Enter 'SSM' to Show Saved Messages.
Enter ':q!' to quit.
Enter your choice: """)
        # connect to central server
        if choice == "0":
            peer.init_client(peer.CENTRAL_SERVER_IP, peer.CENTRAL_SERVER_PORT)
            print("Remember, to start typing, first input an 'i' to enable sending messages!") #inspired by vim
            peer.start_session()
        # connect to another user
        elif choice == "1":
            conn_ip = input("Enter the IP of the user you want to connect to: ")
            conn_port = int(input("Enter the port the user's server is serving on: "))
            peer.init_client(conn_ip=conn_ip, conn_port=conn_port)
            print("Remember, to start typing, first input an 'i' to enable sending messages!") #inspired by vim
            peer.start_session()
        # display all saved messages from the user database
        elif choice == "SSM":
            peer.show_saved_msgs()
        # quit the program
        elif choice == ":q!":
            print("Thank for being a peer!")
            break
        else:
            print("That wasn't a valid choice...please read carefully and try again!")