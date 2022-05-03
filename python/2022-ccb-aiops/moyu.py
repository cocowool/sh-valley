# 2022 AIOPS 摸鱼之旅

from dataclasses import field
from distutils.log import error
import json, datetime, requests, os
from numpy import empty
from kafka import KafkaConsumer
from scipy.stats import kendalltau
import pandas as pd
import numpy as np
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
    failure_timestamp = 1647754788
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

# 将正常的数据按指标输出
def prepare_data():
    # 正常数据文件
    file_name = '/Users/shiqiang/Downloads/2022-ccb-aiops/data_normal/cloudbed-1/metric/node/kpi_cloudbed1_metric_0319.csv'
    f = open(file_name, 'r', encoding='utf-8')
    line = f.readline()
    normal_data = []

    while line:
        # print(line, end='')
        line = f.readline().strip()
        fields = line.split(',')
        if len(fields) > 1:
            if fields[1] == 'node-1' and fields[2] == 'system.cpu.pct_usage':
                print(line)
                normal_data.append({
                    "timestamp": fields[0],
                    "cmdb_id": fields[1],
                    "kpi_name": fields[2],
                    "value": fields[3]
                })


    # print(normal_data)
    f.close()

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

    # 正常数据文件
    # file_name = '/Users/shiqiang/Downloads/2022-ccb-aiops/data_normal/cloudbed-1/metric/node/kpi_cloudbed1_metric_0319.csv'

    df = pd.read_csv(file_name, index_col='timestamp', parse_dates=True)
    print(df)

    adf = df[ df['cmdb_id'].str.contains('node-4')]
    bdf = adf[ adf['kpi_name'].str.contains('system.cpu.pct_usage')]
    print(bdf)

    cdf = bdf.drop('cmdb_id', axis=1)
    cdf = cdf.drop('kpi_name', axis=1)
    cdf.index = pd.to_datetime(cdf.index)
    cdf = validate_series(cdf)
    print(cdf)

    threshold_ad = ThresholdAD(high=20, low=0)
    anomalies = threshold_ad.detect(cdf)
    print(anomalies)

    plot(cdf, anomaly=anomalies, ts_linewidth=1, ts_markersize=3, anomaly_markersize=5, anomaly_color='red', anomaly_tag="marker")
    plt.show()

    # plt.figure()
    # x = bdf.index
    # # y = appmon['sr']
    # # y = appmon['rr']
    # y = bdf['value']
    # plt.plot(x,y)
    # plt.show()
    # print(df['kpi'])
    # print(df["value"])
    # print(df.iloc[:,[0,-1]][df[df.T.index[2]] == 'system.cpu.pct_usage'])
    # plot(df["value"])
    # df_transformed = RollingAggregate(agg='quantile',agg_params={"q": [0.25, 0.75]}, window=5).transform(df)
    # adf = validate_series(adf)
    # plot(adf)
    # pass

# 将 10 份 Metric 数据按照指标绘制到一张图上
def plt_metrics():
    normal_data_prefix = '/Users/shiqiang/Downloads/2022-ccb-aiops/data_normal/'
    faults_data_prefix = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/'

    normal_data_lists = ['cloudbed-1/metric/node/kpi_cloudbed1_metric_0319.csv', 'cloudbed-2/metric/node/kpi_cloudbed2_metric_0319.csv', 'cloudbed-3/metric/node/kpi_cloudbed3_metric_0319.csv']

    faults_data_lists = ['cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv', 'cloudbed-2/metric/node/kpi_cloudbed2_metric_0320.csv', 'cloudbed-3/metric/node/kpi_cloudbed3_metric_0320.csv']

    # 0320 Test File
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv'
    # 0321 Test File
    test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/node/kpi_cloudbed1_metric_0321.csv'

    df = pd.read_csv( test_file )
    
    node_list = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5']
    colors = ['red', 'blue', 'green', 'orange', 'black']
    # CPU 故障
    # cloud_error = {1647754788:'node-4,node CPU FAIL', 1647755511: 'node-6,node CPU FAIL', 1647767561:'node-4,node CPU UP'}

    # 0320 磁盘故障
    # cloud_error = {1647749271: 'node-1, disk read io error', 1647753199: 'node-2 disk write io error', 1647769222: 'node-5 disk write io error', 1647776146: 'node-4, disk read io error', 1647784337: 'node-1, disk space error', 1647788164: 'node-3, disk read io error'}

    # 0321 磁盘故障
    cloud_error = {1647830276: 'node-4, disk space error', 1647852107: 'node-5, disk space error', 1647865567: 'node-3, disk space error', 1647875729: 'node-4, disk space error'}


    # print(cloud_error[1647754788])
    # for i in cloud_error:
    #     print(i)

    # print( df['value'].max() )

    kpi_list = df['kpi_name'].unique()
    for subplot in range(0, len(kpi_list)):
        if 'disk' in kpi_list[subplot] or '.io.' in kpi_list[subplot]:
        # if 'cpu' in kpi_list[subplot] or 'load' in kpi_list[subplot]:
            print(kpi_list[subplot])

            fig = plt.figure(figsize=(14,8))
            plt.rcParams['font.sans-serif'] = 'Monaco'
            # ax = fig.add_subplot(len(kpi_list),1,subplot+1)
            bdf = df[ df['kpi_name'].str.contains(kpi_list[subplot]) ]

            j = 0
            # plt.figure()
            for i in node_list:
                cdf = bdf[ bdf['cmdb_id'].str.contains(i)]
                plt.plot(cdf['timestamp'], cdf['value'], c=colors[j], label=i)
                j += 1

            for i in cloud_error:
                plt.plot(i, cdf['value'].max(), 'o')
                plt.text(i,cdf['value'].max(),cloud_error[i],ha = 'center',va = 'bottom',fontsize=7,rotation=90)

            plt.xlabel('Timestamp')
            plt.ylabel(kpi_list[subplot])
            plt.legend(loc='best')
            plt.show()

    

    # bdf.plot( figsize =(10,6), alpha = 0.5)
    # plt.show()

    # print( df['cmdb_id'].to_list() )
    # bdf = pd.DataFrame(df['cmdb_id'].to_list(), columns = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5'])


    # pd.pivot_table( bdf, index=['timestamp'] )
    # print(bdf)

if __name__ == '__main__':
    # print(timestampFormat(1647723540))

    # 对比 Metric 并绘图
    plt_metrics()

    # load_heads()
    # print("Test")
    # adtk_test()

    # 根据指标加载正常数据
    # prepare_data()

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