from kafka import KafkaConsumer
import time, json, requests, os, random, sys, getopt

# 作为比赛专用调试代码，尝试提交并记录日志

# 提交答案服务域名或IP, 将在赛前告知
HOST = "http://10.3.2.40:30083"

# 团队标识, 可通过界面下方权限获取, 每个ticket仅在当前赛季有效，如未注明团队标识，结果不计入成绩
TICKET = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTA3MzQ5Mjg3NzU0MTc4NjE4IiwiaWF0IjoxNjUwNTUwMzgwLCJ0aWNrZXQiOnsidGlkIjoiMTUwNzM0OTI4Nzc1NDE3ODYxOCIsImNpZCI6IjE0OTYzOTg1MjY0Mjk3MjQ3NjAiLCJzZWFzb24iOiIxIiwic3RhcnQiOiIxNjUwMzg0MDAwMDAwIiwiZW5kIjoiMTY1MjYzMDM5OTAwMCJ9LCJpc3MiOiJCaXpzZWVyIiwiZXhwIjoxNjUyNjMwMzk5fQ.wY7GzSh7cEM-IeP1pUsZiEzOXzg6FzEh3wKHk4j4KwMEeo9TgpLDWt7Evk-NrIvBOL6JdkN2xmP5eAg4FspWkw"

NODE_FAILURE_TYPE = ['node 磁盘读IO消耗', 'node 磁盘空间消耗', 'node 磁盘写IO消耗', 'node 内存消耗', 'node节点CPU故障', 'node节点CPU爬升']
SERVICE_FAILURE_TYPE = ['k8s容器cpu负载', 'k8s容器读io负载', 'k8s容器进程中止', 'k8s容器内存负载', 'k8s容器网络丢包', 'k8s容器网络延迟', 'k8s容器网络资源包损坏', 'k8s容器网络资源包重复发送', 'k8s容器写io负载']

# 处理模式，调试用本地模式，部署用生产模式，默认为生产模式
# pro 表示生产模式
# dev 表示测试模式
PROCESS_MODE = 'pro'

# 记录提交日志
def submit_log(message):
    startname = time.strftime('%Y%m%d', time.localtime(time.time()))
    log_path = '/data/logs/'
    # log_path = './'
    log_file = startname + '-debug.log'

    # if not os.path.exists(log_path + log_file ):
    f = open(log_path + log_file, 'a')
    # else:
    f.write(message)
    f.close()

# 结果提交代码
def submit(ctx):
    assert (isinstance(ctx, list))
    assert (len(ctx) == 2)
    assert (isinstance(ctx[0], str))
    assert (isinstance(ctx[1], str))
    data = {'content': json.dumps(ctx, ensure_ascii=False)}
    r = requests.post(
        url='%s/answer/submit' % HOST,
        json=data,
        headers={"ticket": TICKET}
    )
    return r.text

# Kafka 消费方法
def kafka_consumer():
    CONSUMER = KafkaConsumer(
        'kpi-1c9e9efe6847bc4723abd3640527cbe9',
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
    j = 0
    for message in CONSUMER:
        j += 1
        data = json.loads(message.value.decode('utf8'))
        data = json.loads(data)
        if data.__contains__('cmdb_id') and data.__contains__('kpi_name'):
            if data['kpi_name'] == 'system.cpu.pct_usage' and float(data['value']) > 60:
                print("Catch CPU Error !")
                cpu_pct(data, i)
                i = i + 1

# 消费本地文件的方式，通过读取文件内容来分析异常点
def local_consumer():
    print('Local Consumer Mode !')
    test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv'

    f = open(test_file, 'r', encoding='utf-8')
    line = f.readline()
    match_data = {}
    i = 1

    while line:
        line = f.readline().strip()
        # print(line, end='')
        fields = line.split(',')
        if len(fields) > 1:
            if 'trace_jaeger' in test_file:
                pass
            elif 'log_filebeat' in test_file:
                pass
            elif 'kpi_' in test_file:
                match_data["timestamp"] = fields[0]
                match_data["cmdb_id"] = fields[1]
                match_data["kpi_name"] = fields[2]
                match_data["value"] = fields[3]
            elif 'metric_service' in test_file:
                match_data["service"] = fields[0]
                match_data["timestamp"] = fields[1]
                match_data["rr"] = fields[2]
                match_data["sr"] = fields[3]
                match_data["mrt"] = fields[4]
                match_data["count"] = fields[5]                

        data_process(match_data)

    f.close()    


# 处理数据，按条接收并处理数据，屏蔽 Kafka 和本地文件的差异
# 记录开始处理的时间，记录处理的数据量
def data_process( data ):
    print(data)

    adtk_cpu(data)
    pass

def adtk_cpu(data):
    pass

# 分析CPU故障场景
def cpu_pct(data, i):
    if float(data['value']) > 20:
        # node节点CPU故障
        # print(data)
        res = submit([data['cmdb_id'], SERVICE_FAILURE_TYPE[4]])
        log_message = 'The ' + str(i) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
        log_message += 'Content: [' + data['cmdb_id'] + ', ' + NODE_FAILURE_TYPE[4] + '], Result: ' + res + '\n'
        log_message += 'Metric : ' + data + '\n'
        submit_log(log_message)
        print(res)

# 仅打印 Kafka 中的内容
def kafka_print():
    CONSUMER = KafkaConsumer(
        'kpi-1c9e9efe6847bc4723abd3640527cbe9',
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
    j = 0
    for message in CONSUMER:
        j += 1
        data = json.loads(message.value.decode('utf8'))
        data = json.loads(data)
        print(data)



# 测试用的方法
def test():
    # print(random.choice(SERVICE_FAILURE_TYPE))
    ops_str = '{"service":"frontend-http","timestamp":"1650985740","rr":"100.0","sr":"100.0","mrt":"46.791044776119406","count":"135"}'
    print(ops_str)
    data = json.loads(ops_str)
    print(data)
    print(data['timestamp'])

if __name__ == '__main__':
    print("2022 CCB AIOPS Match by " + sys.argv[0])
    opts, args = getopt.getopt(sys.argv[1:], "m:h:", ["mode", "help"])

    for o, a in opts:
        if o in ("-h", "--help"):
            print("Usage: python3 aimoyu.py -m PRODUCT/DEV")
        if o in ("-m", "--mode"):
            PROCESS_MODE = a

    if PROCESS_MODE == 'dev':
        local_consumer()
    else:
        kafka_consumer()

    # print(PROCESS_MODE)
    # 支持命令行参数，方便调试
    # kafka_consumer()
# submit_log()
# kafka_print()

# i = 1
# log_message = 'The ' + str(i) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
# log_message += 'Content: [service, ' + random.choice(SERVICE_FAILURE_TYPE) + '], Result: ' + '\n'

# print(log_message)
# submit_log(log_message)