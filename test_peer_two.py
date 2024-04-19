from peer import Peer

peer_two = Peer(header_len=10, username="Super Joe")

peer_two.init_server(serv_ip="127.0.0.1", serv_port=41000)
input("CONTINUE WHEN READY")
peer_two.init_client(conn_ip="127.0.0.1", conn_port=40000)

peer_two.start_session()
