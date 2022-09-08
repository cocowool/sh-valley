import time
import sys

import stomp

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        # print('received a message "%s"' % frame.body)
        print(f"message: headers:{frame.headers['destination']}, message:{frame.body}")

conn = stomp.Connection( [('localhost',61613), ('localhost',61614)] )
conn.set_listener('', MyListener())
conn.connect('admin', 'admin', wait=True)
# conn.connect('admin', 'admin', wait=True, headers = {'client-id' : 'qmsg_consumer'})
conn.subscribe(destination='/queue/test', id=1, ack='auto')

while True:
    time.sleep(5)
#     conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')

# conn.disconnect()