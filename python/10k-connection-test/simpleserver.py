#codeing=utf-8

import socket
import time

BUF_SIZE = 1024
host = 'localhost'
port = 8081

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind( (host, port) )
server.listen(10)
client, address = server.accept()
while True:
    client.send( "ok\n".encode('utf-8') )
    time.sleep(1)