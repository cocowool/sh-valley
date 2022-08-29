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
conn.subscribe(destination='/topic/test', id=1, ack='auto')

while True:
    time.sleep(5)
#     conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')

# conn.disconnect()