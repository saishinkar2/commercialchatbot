import socket, threading

HEADER_LENGTH, IP, PORT = 10, "localhost", 8000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind ((IP, PORT))
server_socket.listen()

active_client, waiting_clients = None, []

def send_message(sock, msg):
    try:
        sock.send(f"{len(msg):<{HEADER_LENGTH}}".encode('utf-8') + msg.encode('utf-8'))
    except: return False
    return True

def receive_message(sock):
    try:
        header = sock.recv(HEADER_LENGTH)
        if not header: return False
        length = int(header.decode('utf-8').strip())
        return {'header': header, 'data': sock.recv(length)}
    except: return False

def handle_client(sock):
    global active_client
    while True:
        msg = receive_message(sock)
        if not msg: break

        data = msg['data'].decode('utf-8')
        print(f"Received: {data}")

        if data == ".queue":
            pos = waiting_clients.index(sock) + 1 if sock in waiting_clients else 0
            send_message(sock, f"You are number {pos} in the waiting room." if pos else "You are active.")
        elif sock == active_client:
            send_message(active_client, data)
        else:
            print(f"Waiting client: {data}")
            if active_client: send_message(active_client, f"Message from waiting client: {data}")

    sock.close()
    if sock in waiting_clients: waiting_clients.remove(sock)
    active_client = None

    if waiting_clients:
        active_client = waiting_clients.pop(0)
        send_message(active_client, "It's your turn.")
        threading.Thread(target=handle_client, args=(active_client,), daemon=True).start()

def accept_connections():
    global active_client
    while True:
        sock, _ = server_socket.accept()
        if active_client is None:
            active_client = sock
            send_message(sock, "You are connected.")
            threading.Thread(target=handle_client, args=(sock,), daemon=True).start()
        else:
            waiting_clients.append(sock)
            threading.Thread(target=handle_client, args=(sock,), daemon=True).start()
            send_message(sock, f"Waiting room, position {len(waiting_clients)}.")

def start_message():
    global active_client
    while True:
        msg = input("=>")
        if msg and active_client:
            if msg == ".kick":
                active_client.close()
                active_client = None
            elif msg == ".room":
                print(f"{len(waiting_clients)} in the waiting room.")
            else:
                send_message(active_client, msg)
        elif not active_client:
            print("No active client.")

threading.Thread(target=accept_connections, daemon=True).start()
start_message()
