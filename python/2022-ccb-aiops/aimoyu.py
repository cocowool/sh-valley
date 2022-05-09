from kafka import KafkaConsumer
import time, json, requests, os, random, sys, getopt, datetime, re
import pandas as pd
from pandas import DataFrame, DatetimeIndex
from adtk.data import validate_series
from adtk.transformer import RollingAggregate
from adtk.transformer import DoubleRollingAggregate
from adtk.visualization import plot
from adtk.detector import ThresholdAD
from adtk.detector import QuantileAD
from adtk.detector import GeneralizedESDTestAD
from adtk.detector import LevelShiftAD
from adtk.detector import PersistAD
from adtk.detector import VolatilityShiftAD
from adtk.detector import CustomizedDetectorHD

# 作为比赛专用调试代码，尝试提交并记录日志

# 定义一个单例通用对象，用于传入 kpi、检测方法、样本时间，以及保存指标的对象
class MetaClass( type ):
    def __init__(self, name, bases, dict):
        super(MetaClass, self).__init__(name, bases, dict)
        self._instance = None

    def __call__(self, *args, **kwds):
        if self._instance is None:
            self._instance = super(MetaClass, self).__call__(*args, **kwds)
        return self._instance

class DetectObject( object, metaclass = MetaClass):
    NODE_LIST = [
        "node-1",
        "node-2",
        "node-3",
        "node-4",
        "node-5",
        "node-6"]

    SERVICE_LIST = ['cartservice','productcatalogservice','recommendationservice','shippingservice','adservice','checkoutservice','frontend','currencyservice','emailservice','paymentservice']
    
    KPI_LIST = [ 
        {"kpi_name":"system.cpu.pct_usage", "sample_time":0, "failure_type":"node节点CPU故障", "function_name" : 'threshold_detect', "parameter" : 60},
        # {"kpi_name":"system.cpu.pct_usage", "sample_time":120, "failure_type":"node节点CPU故障", "function_name" : 'maxmin_detect', "parameter" : 60},
        # {"kpi_name":"system.cpu.pct_usage", "sample_time":5, "failure_type":"node节点CPU故障", "function_name" : 'spike_detect', "parameter" : 60},
        # system.io.rkb_s 设备每秒读的 kibibytes 的数量
        {"kpi_name":"system.io.rkb_s","sample_time":0, "failure_type":"node 磁盘读IO消耗" , "function_name" : 'threshold_detect', "parameter" : 100000},
        {"kpi_name":"system.io.await","sample_time":0, "failure_type":"node 磁盘写IO消耗" , "function_name" : 'threshold_detect', "parameter" : 198},
        {"kpi_name":"system.disk.pct_usage","sample_time":5, "failure_type":"node 磁盘空间消耗" , "function_name" : 'threshold_detect', "parameter" : ''}
        ]

    SERVICE_KPI_LIST = [
        # > 20
        # {"kpi_name":"container_cpu_usage_seconds","sample_time":120},
        # > 500
        {"kpi_name":"container_cpu_cfs_throttled_seconds","sample_time":5, "failure_type" : "k8s容器cpu负载" },
        # # # >= 0.8
        {"kpi_name":"container_network_receive_packets_dropped.eth0", "sample_time" : 5, "failure_type": "k8s容器网络资源包损坏"},
        # # # > 3000
        {"kpi_name":"container_fs_writes_MB./dev/vda", "sample_time": 5, "failure_type": "k8s容器写io负载"},
        # # # > 5000
        {"kpi_name" : "container_fs_reads./dev/vda", "sample_time" : 5, "failure_type" : "k8s容器读io负载"},
        # # # > 95
        {"kpi_name" : "container_memory_failures.container.pgmajfault", "sample_time" : 5, "failure_type" : "k8s容器内存负载"},
        # # # istio_requests.grpc.200.0.0 > 3 , k8s容器网络延迟 , service
        {"kpi_name" : "istio_requests.grpc.200.0.0", "sample_time" : 5, "failure_type" : "k8s容器网络延迟"},
        # # # > 增量大于8
        # {"kpi_name" : "container_file_descriptors", "sample_time" : 10, "failure_type" : "k8s容器读io负载"},

    ]
    START_TIME = ''
    PD_LIST = {}
    
    def __init__(self):
        for i in self.NODE_LIST:
            # self.PD_LIST.append

            kpi_dict = {}
            # 将 Node 指标构建存储对象
            for j in self.KPI_LIST:
                j["pd"] = pd.DataFrame
                kpi_dict[j["kpi_name"]] = {"pd": pd.DataFrame(), "sample_time": j["sample_time"], "sample_count": 0, "submit_count": 0, "prev_timestamp" : 0, "failure_type":j["failure_type"], "function_name" : j["function_name"], "parameter" : j["parameter"] }

            self.PD_LIST[i] = kpi_dict

        for i in self.SERVICE_LIST:
            kpi_dict = {}
            for j in self.SERVICE_KPI_LIST:
                j["pd"] = pd.DataFrame
                kpi_dict[j["kpi_name"]] = {"pd": pd.DataFrame(), "sample_time": j["sample_time"], "sample_count": 0, "submit_count": 0, "prev_timestamp" : 0, "failure_type":j["failure_type"] }

            self.PD_LIST[i] = kpi_dict

    def getPd(self, cmdb_id, kpi_name):
        if cmdb_id in self.PD_LIST and kpi_name in self.PD_LIST[cmdb_id]:
            return self.PD_LIST[cmdb_id][kpi_name]
        else:
            return False

    def setPd(self, cmdb_id, kpi_name, pd):
        self.PD_LIST[cmdb_id][kpi_name] = pd 

    def getKpi(self):
        return self.KPI_LIST

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

SUBMIT_COUNT = 0

# 将时间戳转换为可读时间格式
def timestampFormat(timestamp):
    dateArray = datetime.datetime.utcfromtimestamp(timestamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")    

    return otherStyleTime

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

# Kafka 消费方法
def kafka_consumer():
    CONSUMER = KafkaConsumer(
        'kpi-1c9e9efe6847bc4723abd3640527cbe9',
        # 'metric-1c9e9efe6847bc4723abd3640527cbe9',
        # 'trace-1c9e9efe6847bc4723abd3640527cbe9',
        # 'log-1c9e9efe6847bc4723abd3640527cbe9',
        bootstrap_servers=['10.3.2.41', '10.3.2.4', '10.3.2.36'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        security_protocol='PLAINTEXT'
    )

    print("Begin Kafka Consuming")
    # i = 0
    # j = 0
    for message in CONSUMER:
        # j += 1
        data = json.loads(message.value.decode('utf8'))
        data = json.loads(data)
        data_process(data)

        # if data.__contains__('cmdb_id') and data.__contains__('kpi_name'):
        #     if data['kpi_name'] == 'system.cpu.pct_usage' and float(data['value']) > 60:
        #         print("Catch CPU Error !")
        #         cpu_pct(data, i)
        #         i = i + 1

# 以文佳件方式消费数据
def local_folder_consumer():
    metric_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/'

    # metric_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/data_normal/cloudbed-1/metric/container'

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

# 消费本地文件的方式，通过读取文件内容来分析异常点
def local_consumer(test_file):
    print('Local Consumer Mode !')
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220320/cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv'
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/node/kpi_cloudbed1_metric_0321.csv'
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/container/kpi_container_cpu_cfs_throttled_seconds.csv'
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/container/kpi_container_network_receive_packets_dropped.csv'

    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/container/kpi_container_fs_writes_MB.csv'

    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/container/kpi_container_fs_reads.csv'

    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/container/kpi_container_memory_failures.csv'

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
    if PROCESS_MODE == 'dev':
        pass
    else:
        print(data)

    adtk_common(data)

    # MERGE From Wanglei
    # maxmin_node_mem(data)
    # MERGE From Wanglei End

    # moyu_detect(data)

# 固定阈值检测算法
# apd , DetectObject 中初始化的 PD_LIST 对象
# data , 需要处理的数据
# silent_period 静默时间，探测到异常之后连续多长时间不上报
def threshold_detect(apd, data, silent_period = 1200):
    global SUBMIT_COUNT

    if float(data['value']) > float(apd["parameter"]):
        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > silent_period:
            res = submit([data['cmdb_id'], apd["failure_type"] ])
            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
            log_message += 'Content: [' + data['cmdb_id'] + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
            log_message += 'Metric : ' + json.dumps(data) + '\n'
            submit_log(log_message)
            print(res)
            SUBMIT_COUNT += 1
            apd["prev_timestamp"] = data['timestamp']

# 支持设置一个硬基线
# 按照 window 取平均值和标准差，如果当前值与均值差异大于三倍标准差，认为是异常值
# 支持按照同比增长百分比设置阈值（考虑分子为零的情况）
def spike_detect(apd, data, sp_window = 5):
    # print(data)
    # # print( apd["pd"]["value"].rolling(window = sp_window, closed = 'left' ))
    # print( apd["pd"]['value'] )
    # print( apd["pd"]['value'][-6:-1] )
    # print( apd["pd"]['value'][-6:-1].mean() )

    # print( data['cmdb_id'] + ':' + str(data['value']) + ' - ' + str(apd["pd"]['value'][-2]) + ' = ' + str( (float(data['value']) - float(apd["pd"]['value'][-2]) ) / float(apd["pd"]['value'][-2]) ) )
    if (float(data['value']) - float(apd["pd"]['value'][-2]) ) / float(apd["pd"]['value'][-2]) >  2.7:
        print(data)

    # print( apd["pd"]["value"].rolling(window = sp_window, closed = 'left' ).mean())
    # print( apd["pd"]["value"].rolling(window = sp_window, closed = 'left' ).std())
    # time.sleep(10)
    # if float(data['value']) - apd['pd']["value"][-2] > 2:
    #     if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 600:
    #         res = submit([data['cmdb_id'], apd["failure_type"] ])
    #         log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
    #         log_message += 'Content: [' + data['cmdb_id'] + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
    #         log_message += 'Metric : ' + json.dumps(data) + '\n'
    #         submit_log(log_message)
    #         print(res)
    #         SUBMIT_COUNT += 1
    #         apd["prev_timestamp"] = data['timestamp']

# adtk 检测方法
def adtk_detect(apd, data):
    s = validate_series(apd["pd"])
    
    persist_ad = PersistAD(window = 10, c = 30, side='positive', agg='mean')
    anomalies = persist_ad.fit_detect(s)

    if(anomalies.iloc[-1]['value'] == True):
        print(data)
    # print()
    # time.sleep(1)

# 改写 maxmin_node_mem 函数
def maxmin_detect(apd, data):
    global SUBMIT_COUNT
    apd["current_max_minus_min"] = apd["pd"]["value"].max() - apd["pd"]["value"].min()

    if data['cmdb_id'] == "node-4":

        if 'last_max_minus_min' not in apd:
            apd["last_max_minus_min"] = apd["current_max_minus_min"]

        print("current:" +  str(apd["current_max_minus_min"]))
        print("last:" +  str(apd["last_max_minus_min"]))
        print("current/last:" +  str(apd["current_max_minus_min"] / apd["last_max_minus_min"]))

        if ( apd["current_max_minus_min"] / apd["last_max_minus_min"]) > 1.7:
            res = submit([data['cmdb_id'], apd["failure_type"] ])
            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
            log_message += 'Content: [' + data['cmdb_id'] + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
            log_message += 'Metric : ' + json.dumps(data) + '\n'
            submit_log(log_message)
            print(res)
            SUBMIT_COUNT += 1
            apd["prev_timestamp"] = data['timestamp']

# 通用的异常检测方法，支持数据传入、指定 KPI 
def adtk_common(data):
    global SUBMIT_COUNT
    obj_a = DetectObject()
    # print(data)

    # 判断 Node 类型的故障
    if obj_a.getPd(data['cmdb_id'], data['kpi_name']):
        t_series = pd.Series({"value" : float(data['value'])}, name=timestampFormat(int(data['timestamp'])) )
        apd = obj_a.getPd(data['cmdb_id'], data['kpi_name'])
        apd["pd"] = apd["pd"].append( t_series )
        apd["sample_count"] = apd["sample_count"] + 1

        if apd['sample_count'] > apd['sample_time']:
            apd["pd"].index = pd.to_datetime( apd["pd"].index )
            apd["pd"] = validate_series( apd["pd"] )

            if data['kpi_name'] == 'system.io.rkb_s':
                eval(apd["function_name"])(apd, data)
            elif data['kpi_name'] == 'system.io.await':
                eval(apd["function_name"])(apd, data)
            elif data['kpi_name'] == 'system.cpu.pct_usage':
                eval(apd["function_name"])(apd, data)
            elif data['kpi_name'] == 'system.disk.pct_usage':
                if data['cmdb_id'] == "node-6":
                    return False

                if float(data['value']) - apd['pd']["value"][-2] > 5:
                    if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 1200:
                        res = submit([data['cmdb_id'], apd["failure_type"] ])
                        log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                        log_message += 'Content: [' + data['cmdb_id'] + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                        log_message += 'Metric : ' + json.dumps(data) + '\n'
                        submit_log(log_message)
                        print(res)
                        SUBMIT_COUNT += 1
                        apd["prev_timestamp"] = data['timestamp']
                    
                elif float(data['value']) - apd['pd']["value"][-3] > 2:
                    if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 1200:
                        res = submit([data['cmdb_id'], apd["failure_type"] ])
                        log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                        log_message += 'Content: [' + data['cmdb_id'] + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                        log_message += 'Metric : ' + json.dumps(data) + '\n'
                        submit_log(log_message)
                        print(res)
                        SUBMIT_COUNT += 1
                        apd["prev_timestamp"] = data['timestamp']
    
        # obj_a.setPd(data['cmdb_id'], data['kpi_name'], apd)
            # time.sleep(2)

        # print(data['cmdb_id'] + "-" + data['kpi_name'])
        # print(apd)
        # print( obj_a.getPd(data['cmdb_id'], data['kpi_name']) )
    else:
        # 判断 Service 或 Pod 类型的故障
        pattern = re.compile("node-\d.")
        ret = pattern.findall(data['cmdb_id'])
        if ret:
            cmdb_name = data['cmdb_id'].split('.')[1]
            cmdb_key = re.sub("[^A-Za-z]", "", cmdb_name)
            # print(data)

            if obj_a.getPd(cmdb_key, data['kpi_name']):
                t_series = pd.Series({"value" : float(data['value'])}, name=timestampFormat(int(data['timestamp'])) )
                apd = obj_a.getPd(cmdb_key, data['kpi_name'])
                apd["pd"] = apd["pd"].append( t_series )
                apd["sample_count"] = apd["sample_count"] + 1


                if apd['sample_count'] < apd['sample_time']:
                    return True

                if data['kpi_name'] == 'container_cpu_cfs_throttled_seconds':

                    # print(data)
                    if float(data['value']) > 500:
                        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 600:
                            res = submit([cmdb_name, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_name + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            res = submit([cmdb_key, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_key + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            apd["prev_timestamp"] = data['timestamp']
                elif data['kpi_name'] == 'container_network_receive_packets_dropped.eth0':
                    # print(data)
                    if float(data['value']) > 0.8:
                        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 600:
                            res = submit([cmdb_name, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_name + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            res = submit([cmdb_key, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_key + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            apd["prev_timestamp"] = data['timestamp']
                elif data['kpi_name'] == 'container_fs_writes_MB./dev/vda':
                    # print(data)
                    if float(data['value']) > 3000:
                        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 600:
                            res = submit([cmdb_name, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_name + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            res = submit([cmdb_key, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_key + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            apd["prev_timestamp"] = data['timestamp']
                elif data['kpi_name'] == 'container_fs_reads./dev/vda':
                    # if "payment" in data['cmdb_id']:
                    #     return False

                    # print(data)
                    if float(data['value']) > 20000:
                        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 3600:
                            res = submit([cmdb_name, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_name + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            res = submit([cmdb_key, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_key + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            apd["prev_timestamp"] = data['timestamp']
                elif data['kpi_name'] == 'container_memory_failures.container.pgmajfault':
                    if float(data['value']) > 290:
                        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 600:
                            res = submit([cmdb_name, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_name + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            res = submit([cmdb_key, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_key + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            apd["prev_timestamp"] = data['timestamp']
                elif data['kpi_name'] == 'container_file_descriptors':
                    if float(data['value']) - apd['pd']["value"][-3] > 8:
                        if apd["prev_timestamp"] == 0 or int(data['timestamp']) - int(apd["prev_timestamp"]) > 600:
                            res = submit([cmdb_name, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_name + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            res = submit([cmdb_key, apd["failure_type"] ])
                            log_message = 'The ' + str(SUBMIT_COUNT) + ' Submit at ' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '\n'
                            log_message += 'Content: [' + cmdb_key + ', ' + apd["failure_type"] + '], Result: ' + res + '\n'
                            log_message += 'Metric : ' + json.dumps(data) + '\n'
                            submit_log(log_message)
                            print(res)
                            SUBMIT_COUNT += 1

                            apd["prev_timestamp"] = data['timestamp']


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

    obj_a = DetectObject()

    if PROCESS_MODE == 'dev':
        local_folder_consumer()
    else:
        kafka_consumer()
