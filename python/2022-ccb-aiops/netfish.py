from kafka import KafkaConsumer
import time, json, requests, os, random, sys, getopt, datetime, re
import pandas as pd
from pandas import DataFrame, DatetimeIndex

# 框架思路
# 1. 按时间戳分批次读取原始指标数据
# 2. 区分指标，经过训练时间段后，开始进行异常数据的判断，将发现的异常数据压入队列
# 3. 每个时间批次结束后，汇总指标异常的情况，判断是否有故障发生

# 处理模式，调试用本地模式，部署用生产模式，默认为生产模式
# pro 表示生产模式
# dev 表示测试模式
PROCESS_MODE = 'pro'

# 提交答案服务域名或IP, 将在赛前告知
HOST = "http://10.3.2.40:30083"
# 团队标识, 可通过界面下方权限获取, 每个ticket仅在当前赛季有效，如未注明团队标识，结果不计入成绩
TICKET = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTA3MzQ5Mjg3NzU0MTc4NjE4IiwiaWF0IjoxNjUwNTUwMzgwLCJ0aWNrZXQiOnsidGlkIjoiMTUwNzM0OTI4Nzc1NDE3ODYxOCIsImNpZCI6IjE0OTYzOTg1MjY0Mjk3MjQ3NjAiLCJzZWFzb24iOiIxIiwic3RhcnQiOiIxNjUwMzg0MDAwMDAwIiwiZW5kIjoiMTY1MjYzMDM5OTAwMCJ9LCJpc3MiOiJCaXpzZWVyIiwiZXhwIjoxNjUyNjMwMzk5fQ.wY7GzSh7cEM-IeP1pUsZiEzOXzg6FzEh3wKHk4j4KwMEeo9TgpLDWt7Evk-NrIvBOL6JdkN2xmP5eAg4FspWkw"


# 定义一个单例通用对象，用于传入 kpi、检测方法、样本时间，以及保存指标的对象
class MetaClass( type ):
    def __init__(self, name, bases, dict):
        super(MetaClass, self).__init__(name, bases, dict)
        self._instance = None

    def __call__(self, *args, **kwds):
        if self._instance is None:
            self._instance = super(MetaClass, self).__call__(*args, **kwds)
        return self._instance

# 用于 batch_process 的单例对象
# 对象的格式约定
# [ kpi_name : {
#       normal_data: []
#       anonamly_data : []
#   
# }]
class ErrorPoint( object, metaclass = MetaClass):
    EP_LIST = {
        'common' : {
            'start_time' : 0,
            'submit_count' : 0,
            'kpi_count' : 0
        }
    }

    def __init__(self):
        pass

    def getInstance(self):
        return self.EP_LIST

    def setKpi(self, kpi_name, data):
        self.EP_LIST[kpi_name] = data

    def getKpi(self, kpi_name):
        return self.EP_LIST[kpi_name]


# 消费本地文件夹下的文件，支持按照时间顺序依次读取部分内容
def local_folder_consumer():
    metric_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/'

    # 记录开始的时间戳
    start_timestamp = 0
    # 用于存放 csv 生成的 pd 对象
    pd_list = []

    for parent, dir_lists, file_lists in os.walk(metric_folder):
        for file_name in file_lists:
            if file_name.endswith('csv'):
                file_name = os.path.join(parent, file_name)

                if 'trace_jaeger' in file_name:
                    # df = pd.read_csv(file_name)
                    # df = df.sort_values('timestamp')
                    # pd_list.append(df)
                    pass
                elif 'log_filebeat' in file_name:
                    # df = pd.read_csv(file_name)
                    # df = df.sort_values('timestamp')
                    # pd_list.append(df)
                    pass
                elif 'metric_service' in file_name:
                    # df = pd.read_csv(file_name)
                    # df = df.sort_values('timestamp')
                    # pd_list.append(df)
                    pass
                elif 'kpi_' in file_name:
                    # print(file_name)
                    df = pd.read_csv(file_name)
                    df = df.sort_values('timestamp')
                    pd_list.append(df)
                    # local_consumer(file_name)

    # 思路：找出时间戳的最小值、最大值，以时间作为递进值不断循环，循环中每次遍历所有的 pd_item
    start_timestamp = pd_list[1]['timestamp'].min()
    stop_timestamp = pd_list[1]['timestamp'].max()
    current_timestamp = start_timestamp

    while current_timestamp <= stop_timestamp:
        for pd_item in pd_list:
            sdf = pd_item[ pd_item['timestamp'] == current_timestamp ]

            for index, row in sdf.iterrows():
                batch_process(row.to_json())
                
        current_timestamp += 60

def batch_process(data):
    print(data)
    pass


def local_consumer(file_name):
    # print( file_name )
    pass

# Kafka 消费方法
def kafka_consumer():
    AVAILABLE_TOPICS = {
        'kpi-c8f21f1c53704f8040e8fd1eb17c4d01',
        'metric-c8f21f1c53704f8040e8fd1eb17c4d01',
        'trace-c8f21f1c53704f8040e8fd1eb17c4d01',
        'log-c8f21f1c53704f8040e8fd1eb17c4d01'
    }

    CONSUMER = KafkaConsumer(
        'kpi-c8f21f1c53704f8040e8fd1eb17c4d01',
        'metric-c8f21f1c53704f8040e8fd1eb17c4d01',
        'trace-c8f21f1c53704f8040e8fd1eb17c4d01',
        'log-c8f21f1c53704f8040e8fd1eb17c4d01',
        bootstrap_servers=['10.3.2.41', '10.3.2.4', '10.3.2.36'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        security_protocol='PLAINTEXT'
    )

    assert AVAILABLE_TOPICS <= CONSUMER.topics(), 'Please contact admin'
    print('test consumer')
    i = 0
    for message in CONSUMER:
        i += 1
        data = json.loads(message.value.decode('utf8'))
        print(type(data), data)
        batch_process(data)

# 将在线播放的数据按照天保存为文件
def save_data( ):
    AVAILABLE_TOPICS = {
        'kpi-c8f21f1c53704f8040e8fd1eb17c4d01',
        'metric-c8f21f1c53704f8040e8fd1eb17c4d01',
        'trace-c8f21f1c53704f8040e8fd1eb17c4d01',
        'log-c8f21f1c53704f8040e8fd1eb17c4d01'
    }

    CONSUMER = KafkaConsumer(
        'kpi-c8f21f1c53704f8040e8fd1eb17c4d01',
        'metric-c8f21f1c53704f8040e8fd1eb17c4d01',
        'trace-c8f21f1c53704f8040e8fd1eb17c4d01',
        'log-c8f21f1c53704f8040e8fd1eb17c4d01',
        bootstrap_servers=['10.3.2.41', '10.3.2.4', '10.3.2.36'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        security_protocol='PLAINTEXT'
    )

    assert AVAILABLE_TOPICS <= CONSUMER.topics(), 'Please contact admin'

    i = 0
    for message in CONSUMER:
        i += 1
        data = json.loads(message.value.decode('utf8'))
        
        print(type(data), data)
        
        today = time.strftime("%Y-%m-%d", time.localtime() )
        today_file = '/data/logs/aiops-data-' + today + '.log'
        if os.path.exists( today_file):
            f = open( today_file, 'a')
            f.writelines(data + '\n' )
            f.close()
        else:
            f = open( today_file, 'w')
            f.writelines(data + '\n')
            f.close()        

# 记录提交日志
def submit_log(message):
    global PROCESS_MODE
    # print("--------------------")
    # print("Function in submit_log")
    # print("--------------------")

    if PROCESS_MODE == 'dev':
        print(message)
        return "Dev Submit_Log Test !"

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
    global PROCESS_MODE
    # print("--------------------")
    # print("Function in submit_log")
    # print("--------------------")

    if PROCESS_MODE == 'dev':
        print("Submit Cotent")
        print(ctx)
        return "Dev Submit Test !"

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


if __name__ == '__main__':
    print("2022 CCB AIOPS Match Round 2 by " + sys.argv[0])
    opts, args = getopt.getopt(sys.argv[1:], "m:h:", ["mode", "help"])

    for o, a in opts:
        if o in ("-h", "--help"):
            print("Usage: python3 aimoyu.py -m PRODUCT/DEV")
        if o in ("-m", "--mode"):
            PROCESS_MODE = a

    if PROCESS_MODE == 'dev':
        local_folder_consumer()
    elif PROCESS_MODE == 'data':
        save_data()
    else:
        kafka_consumer()

