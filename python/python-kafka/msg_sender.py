from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost:9092'})
p.produce('tran_raw', b'hello world')
p.flush(timeout=30)