# 消费 Kafka 数据

from kafka import KafkaConsumer
import time
import json

CONSUMER = KafkaConsumer(
    # 'kpi-1c9e9efe6847bc4723abd3640527cbe9',
    'metric-1c9e9efe6847bc4723abd3640527cbe9',
    # 'trace-1c9e9efe6847bc4723abd3640527cbe9',
    # 'log-1c9e9efe6847bc4723abd3640527cbe9',
    bootstrap_servers=['10.3.2.41', '10.3.2.4', '10.3.2.36'],
    auto_offset_reset='latest',
    enable_auto_commit=False,
    security_protocol='PLAINTEXT'
)

print("Begin Kafka Consuming")
i = 0
for message in CONSUMER:
    i += 1
    data = json.loads(message.value.decode('utf8'))
    print(type(data), data)
