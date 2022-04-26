from kafka import KafkaConsumer
import time, json

# 作为比赛专用调试代码，尝试提交并记录日志

# 记录提交日志
def submit_log():
    pass

node_failure_type = ['node 磁盘读IO消耗', 'node 磁盘空间消耗', 'node 磁盘写IO消耗', 'node 内存消耗', 'node节点CPU故障', 'node节点CPU爬升']
service_failure_type = ['k8s容器cpu负载', 'k8s容器读io负载', 'k8s容器进程中止', 'k8s容器内存负载', 'k8s容器网络丢包', 'k8s容器网络延迟', 'k8s容器网络资源包损坏', 'k8s容器网络资源包重复发送', 'k8s容器写io负载']

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
    if data.count > 100:
        print(type(data), data)

