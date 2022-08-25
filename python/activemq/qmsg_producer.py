import time
import sys

import stomp

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        print('received a message "%s"' % frame.body)

conn = stomp.Connection()
conn.set_listener('', MyListener())
conn.connect('admin', 'admin', wait=True)
# conn.subscribe(destination='/queue/test_queue', id=1, ack='auto')

while True:
    t=time.gmtime()
    msg=" hello  " + time.strftime("%Y-%m-%d %H:%M:%S",t)
    conn.send(body=msg, destination='/queue/test')
    print(" send : " + msg)
    time.sleep(10)

conn.disconnect()