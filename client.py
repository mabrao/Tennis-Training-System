import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.4.1', 80)) #ip, port

while True:
    msg = s.recv(1024) #buffer
    print(msg.decode('utf-8'))

