# 2022 AIOPS 摸鱼之旅

from dataclasses import field
from distutils.log import error
import json, datetime, requests, os
from numpy import empty
from kafka import KafkaConsumer
from scipy.stats import kendalltau
import pandas as pd
from adtk.data import validate_series
from adtk.transformer import RollingAggregate
from adtk.transformer import DoubleRollingAggregate
from adtk.visualization import plot
from adtk.detector import ThresholdAD
import matplotlib.pyplot as plt


# 提交答案服务域名或IP, 将在赛前告知
HOST = "http://10.3.2.40:30083"

# 团队标识, 可通过界面下方权限获取, 每个ticket仅在当前赛季有效，如未注明团队标识，结果不计入成绩
TICKET = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNTA3MzQ5Mjg3NzU0MTc4NjE4IiwiaWF0IjoxNjUwNTUwMzgwLCJ0aWNrZXQiOnsidGlkIjoiMTUwNzM0OTI4Nzc1NDE3ODYxOCIsImNpZCI6IjE0OTYzOTg1MjY0Mjk3MjQ3NjAiLCJzZWFzb24iOiIxIiwic3RhcnQiOiIxNjUwMzg0MDAwMDAwIiwiZW5kIjoiMTY1MjYzMDM5OTAwMCJ9LCJpc3MiOiJCaXpzZWVyIiwiZXhwIjoxNjUyNjMwMzk5fQ.wY7GzSh7cEM-IeP1pUsZiEzOXzg6FzEh3wKHk4j4KwMEeo9TgpLDWt7Evk-NrIvBOL6JdkN2xmP5eAg4FspWkw"

AVAILABLE_TOPICS = {
    'kpi-1c9e9efe6847bc4723abd3640527cbe9',
    'metric-1c9e9efe6847bc4723abd3640527cbe9',
    'trace-1c9e9efe6847bc4723abd3640527cbe9',
    'log-1c9e9efe6847bc4723abd3640527cbe9'
}

# KPI 名称字典
KPI_LISTS = []

# CONSUMER = KafkaConsumer(
#     'kpi-1c9e9efe6847bc4723abd3640527cbe9',
#     'metric-1c9e9efe6847bc4723abd3640527cbe9',
#     'trace-1c9e9efe6847bc4723abd3640527cbe9',
#     'log-1c9e9efe6847bc4723abd3640527cbe9',
#     bootstrap_servers=['10.3.2.41', '10.3.2.4', '10.3.2.36'],
#     auto_offset_reset='latest',
#     enable_auto_commit=False,
#     security_protocol='PLAINTEXT'
# )

# 将时间戳转换为可读时间格式
def timestampFormat(timestamp):
    dateArray = datetime.datetime.utcfromtimestamp(timestamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")    

    return otherStyleTime

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

# 判断交易码中的系统成功率
def service_check(file_name = ''):
    # 无故障的训练数据
    # service_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/cloudbed-1/metric/service/metric_service.csv'
    # 有故障的训练数据
    service_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/service/metric_service.csv'
    service_file = file_name
    f = open(service_file, 'r', encoding='utf-8')
    line = f.readline()
    apm_data = []
    i = 1

    while line:
        # print(line, end='')
        line = f.readline().strip()
        fields = line.split(',')
        if len(fields) > 1:
            # apm_data.append({
            #     "service": fields[0],
            #     "timestamp": fields[1],
            #     "rr": fields[2],
            #     "sr": fields[3],
            #     "mrt": fields[4],
            #     "count": fields[5]
            # })

            # 如果指标低于100则记录下来
            # @TODO 后续可考虑数据持久化
            if float(fields[3]) < 100:
                apm_data.append({
                    "service": fields[0],
                    "timestamp": fields[1],
                    "rr": fields[2],
                    "sr": fields[3],
                    "mrt": fields[4],
                    "count": fields[5]
                })
                # print(fields)

    f.close()
    return apm_data


# 加载 groundtruth 数据到 pd 数据结构中
def load_groundtruth():
    print("Load groundtruth data")
    groundtruth_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/groundtruth'

    out_file = 'all_groundtruth.csv'

    for parent, _, file_names in os.walk(groundtruth_folder):
        for file_name in file_names:
            if file_name.endswith('csv'):
                df = pd.read_csv( groundtruth_folder + '/' + file_name)
                df.to_csv(groundtruth_folder + '/' + out_file, mode='a', index=False)

    print("Done")
    # pass

# 遍历 cloudbed1 文件夹下的所有日志文件，打印故障时间短的所有日志信息
# 日志格式的特点
# * jaeger timestamp 第一列
# * log timestamp 第二列
# * metric timestamp 第一列
# * metric service timestamp 第二列
def load_heads():
    log_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1'

    # 故障时间点
    failure_timestamp = 1647743133
    # 日志查找的前后时间范围
    find_level = 300

    for parent, dir_lists, file_lists in os.walk(log_folder):
        for file_name in file_lists:
            if file_name.endswith('csv'):
                file_name = os.path.join(parent, file_name)
                print(file_name)
                # f = open(file_name, 'r', encoding='utf-8')
                # line = f.readline()
                # f.close()

                if 'trace_jaeger' in file_name:
                    print(failure_logs(file_name, find_level, failure_timestamp, 0))
                elif 'log_filebeat' in file_name:
                    print(failure_logs(file_name, find_level, failure_timestamp, 1))
                elif 'kpi_' in file_name:
                    print(failure_logs(file_name, find_level, failure_timestamp, 0))
                elif 'metric_service' in file_name:
                    print(failure_logs(file_name, find_level, failure_timestamp, 1))
 
def failure_logs(file_name, find_level, failure_timestamp, timestamp_col):
    f = open(file_name, 'r', encoding='utf-8')
    line = f.readline()
    apm_data = []

    while line:
        # print(line, end='')
        line = f.readline().strip()
        fields = line.split(',')
        if len(fields) > 1:
            if abs(int(fields[timestamp_col]) - failure_timestamp) < find_level:
                print(line)
                # apm_data.append(fields)

    f.close()
    return apm_data

# 测试 ADTK 来验证时间序列
def adtk_test():
    file_name = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv'
    df = pd.read_csv(file_name, index_col='timestamp', parse_dates=True)
    # print(df.cmdb_id)
    # print(df.index)
    df.index = pd.to_datetime(df.index)
    df = validate_series(df)
    print(df)
    adf = df.drop('cmdb_id', axis=1)
    adf = adf.drop('kpi_name', axis=1)
    print(adf)

    bdf = df[ df['kpi_name'].str.contains('system.cpu.pct_usage') ]
    bdf = bdf.drop('cmdb_id', axis = 1)
    bdf = bdf.drop('kpi_name', axis = 1)

    print(bdf)
    
    plot(bdf)

    threshold_ad = ThresholdAD(high=20, low=5)
    anomalies = threshold_ad.detect(bdf)
    plot(bdf, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")


    # plt.figure()
    # x = bdf.index
    # # y = appmon['sr']
    # # y = appmon['rr']
    # y = bdf['value']
    # plt.plot(x,y)
    plt.show()


    # print(df['kpi'])
    # print(df["value"])
    # print(df.iloc[:,[0,-1]][df[df.T.index[2]] == 'system.cpu.pct_usage'])
    # plot(df["value"])
    # df_transformed = RollingAggregate(agg='quantile',agg_params={"q": [0.25, 0.75]}, window=5).transform(df)
    adf = validate_series(adf)
    plot(adf)
    # pass

if __name__ == '__main__':
    load_heads()
    # print("Test")
    # adtk_test()

    # # 加载合并后的 groundtruth 文件
    # groundtruth_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/groundtruth/all_groundtruth.csv'
    # gf = pd.read_csv(groundtruth_folder)
    # # print(gf)

    # med_file_1 = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/service/metric_service.csv'
    # med_file_2 = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-2/metric/service/metric_service.csv'
    # med_file_3 = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-3/metric/service/metric_service.csv'



    # error_apm_1 = service_check(med_file_1)
    # print(error_apm_1)

    # for i in error_apm_1:
    #     print(gf['timestamp'].str.contains(i['timestamp']))


    # error_apm_2 = service_check(med_file_2)
    # print(error_apm_2)

    # for i in error_apm_2:
    #     print(gf['timestamp'].str.contains(i['timestamp']))

    # error_apm_3 = service_check(med_file_3)
    # print(error_apm_3)

    # for i in error_apm_3:
    #     print(gf['timestamp'].str.contains(i['timestamp']))


    # print(error_apm)
    # print(gf['timestamp'].str.contains('1647761243'))
    # print(gf.loc[305])

    # load_groundtruth()