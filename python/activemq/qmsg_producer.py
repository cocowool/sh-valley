import time
import sys

import stomp

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_connecting(self, host_and_port):
        print('Connecting to: ' + host_and_port[0] + ':' + str(host_and_port[1]) + '...')

    def on_message(self, frame):
        print('received a message "%s"' % frame.body)

    def on_disconnected(self):
        print('Disconnected...')
        # connect_and_subscribe(self.conn)

conn = stomp.Connection([('localhost',61611)], reconnect_sleep_initial=5, reconnect_sleep_increase=0.5, reconnect_sleep_jitter=0.1, reconnect_sleep_max=120.0, reconnect_attempts_max=10)
conn.set_listener('logicServerQueue', MyListener())
# conn.start()
conn.connect('admin', 'admin', wait=True)
# conn.subscribe(destination='/queue/test_queue', id=1, ack='auto')

while True:
    t=time.gmtime()
    msg=" hello  " + time.strftime("%Y-%m-%d %H:%M:%S",t)
    conn.send(body=msg, destination='/queue/test', headers={'consumerId': 'qmsg_producer', 'content-length': 200, 'selector': 'ccb'})
    print(" send : " + msg)
    time.sleep(10)

conn.disconnect()