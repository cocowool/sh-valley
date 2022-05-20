from kafka import KafkaConsumer
import time, json, requests, os, random, sys, getopt, datetime, re
import pandas as pd
from pandas import DataFrame, DatetimeIndex

# 框架思路
# 1. 按时间戳分批次读取原始指标数据
# 2. 区分指标，经过训练时间段后，开始进行异常数据的判断，将发现的异常数据压入队列
# 3. 每个时间批次结束后，汇总指标异常的情况，判断是否有故障发生

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

    for parent, dir_lists, file_lists in os.walk(metric_folder):
        for file_name in file_lists:
            if file_name.endswith('csv'):
                file_name = os.path.join(parent, file_name)
                print(file_name)
                # f = open(file_name, 'r', encoding='utf-8')
                # line = f.readline()
                # f.close()

                if 'trace_jaeger' in file_name:
                    pass
                elif 'log_filebeat' in file_name:
                    pass
                elif 'metric_service' in file_name:
                    pass
                elif 'kpi_' in file_name:
                    local_consumer(file_name)

def local_consumer(file_name):
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

def batch_process(data):
    pass


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
    else:
        kafka_consumer()
