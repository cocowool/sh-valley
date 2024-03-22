from confluent_kafka import Consumer


c = Consumer({'bootstrap.servers': 'localhost:9092', 'group.id' : 'test-group'})
c.subscribe(['tran_raw'])

try:
    while True:
        msg = c.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print('Error occured: {}'.format(msg.error()))
        print('Message: {}'.format(msg.value().decode('utf-8')))

except KeyboardInterrupt:
    pass

finally:
    c.close()