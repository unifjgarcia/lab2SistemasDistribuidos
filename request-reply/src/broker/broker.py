import zmq

context = zmq.Context()
poller = zmq.Poller()

# Socket que fala com os CLIENTES (REQ)
client_socket = context.socket(zmq.ROUTER)
client_socket.bind("tcp://*:5555")
poller.register(client_socket, zmq.POLLIN)
client_count = 0

# Socket que fala com os SERVIDORES (REP)
server_socket = context.socket(zmq.DEALER)
server_socket.bind("tcp://*:5556")
poller.register(server_socket, zmq.POLLIN)
server_count = 0

print("[BROKER] Iniciado nas portas 5555 (clientes) e 5556 (servidores)", flush=True)

while True:
    socks = dict(poller.poll())

    # Mensagem vindo de algum CLIENTE → encaminha para o SERVIDOR
    if socks.get(client_socket) == zmq.POLLIN:
        client_count += 1
        msg = client_socket.recv_multipart()   # pega TODOS os frames
        server_socket.send_multipart(msg)      # encaminha TODOS os frames
        print(f"[BROKER] Mensagem de cliente encaminhada ({client_count})", flush=True)

    # Mensagem vindo de algum SERVIDOR → encaminha para o CLIENTE correto
    if socks.get(server_socket) == zmq.POLLIN:
        server_count += 1
        msg = server_socket.recv_multipart()
        client_socket.send_multipart(msg)
        print(f"[BROKER] Mensagem de servidor encaminhada ({server_count})", flush=True)