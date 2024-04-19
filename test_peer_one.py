from peer import Peer

peer_one = Peer(header_len=10, username="Bob")

peer_one.init_server(serv_ip="127.0.0.1", serv_port=40000)
input("CONTINUE WHEN READY")
peer_one.init_client(conn_ip="127.0.0.1", conn_port=41000)
input("CONTINUE WHEN READY")

peer_one.start_session()
