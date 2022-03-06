#codeing: utf-8
from __future__ import print_function
from gevent.server import StreamServer
import signal
import gevent
from gevent.signal import signal
# import signal

# sleeptime = 60

def handle(socket, address):
    # print(address)
    # data = socket.recv(1024)
    # print(data)
    socket.sendall( bytes('Welcome to the echo server! Type quit to exit.\r\n', 'utf-8') )
    fileobj = socket.makefile()
    while True:
        # line = fileobj.readline()
        # if line.strip().lower() == 'quit':
        #     print ("client quit")
        #     break
        # fileobj.write(line)
        # fileobj.flush()
        # print ("echoed %r" % line)

        gevent.sleep(sleeptime)
        try:
            socket.send( bytes("ok\n",'utf-8') )
        # except KeyboardInterrupt:
        #     print("Server Close")
        # except socket.error:
        #     print("Server Close")
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
    
    gevent.signal_handler(signal.SIGTERM, server.close)
    # gevent.signal(signal.SIGQUIT, server.close)

    server.serve_forever()