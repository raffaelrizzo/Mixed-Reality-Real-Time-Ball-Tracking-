import socket

HOST = ''
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

while True:
    rcv, addr = sock.recvfrom(1024)
    print(rcv, addr)

sock.close()