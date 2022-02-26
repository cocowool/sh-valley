#codeing: utf-8
from __future__ import print_function
from gevent.server import StreamServer
import gevent
from gevent.signal import signal
# import signal

# sleeptime = 60

def handle(socket, address):
    # print(address)
    # data = socket.recv(1024)
    # print(data)
    while True:
        gevent.sleep(sleeptime)
        try:
            socket.send( bytes("ok\n",'utf-8') )
        except Exception as e:
            print(e)

if __name__ == "__main__":
    import sys
    port = 80
    if len(sys.argv) > 2:
        port = int(sys.argv[1])
        sleeptime = int(sys.argv[2])
    else:
        print("Tow parameters needed!")
        sys.exit(1)
    # default backlog is 256

    server = StreamServer(('0.0.0.0', port), handle, backlog=4096)
    gevent.signal(signal.SIGQUIT, server.close)
    server.serve_forever()