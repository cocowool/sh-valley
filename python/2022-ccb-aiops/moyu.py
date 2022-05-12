# 2022 AIOPS 摸鱼之旅

from dataclasses import field
from distutils.log import error
import json, datetime, requests, os, time, random, getopt, sys
from pyparsing import alphanums
from posixpath import split
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
from adtk.detector import PersistAD
import matplotlib.pyplot as plt
import matplotlib as matplotlib
import matplotlib.patches as patches

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

def random_colormap(N: int,cmaps_='gist_ncar',show_=False):
    # 从颜色图（梯度多）中取N个
    # test_cmaps = ['gist_rainbow', 'nipy_spectral', 'gist_ncar']
    cmap = matplotlib.colors.ListedColormap(plt.get_cmap(cmaps_)(np.linspace(0, 1, N)))
    if show_:
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(1, 1, figsize=(5, 1))
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        plt.show()
    return cmap

# 画出故障点期间，多个指标的聚合图，每个指标一个子图
# 从而来分析关联性
def error_plt( plot_folder = 'node' ):
    metric_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/' + plot_folder

    truth_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/groundtruth/groundtruth-k8s-1-2022-03-21.csv'
    tdf = pd.read_csv( truth_file )
    # tdf = tdf[ ~ tdf['level'].str.contains('node')]
    tdf = tdf[ ~ tdf['level'].str.contains('pod')]
    tdf = tdf[ ~ tdf['level'].str.contains('service')]

    # 需要忽略的 KPI
    ignore_kpi_lists = ['istio_requests.grpc.0.2.0', 'istio_requests.grpc.200.0.0', 'istio_requests.grpc.200.4.0', 'istio_requests.http.200.', 'istio_requests.http.202.', 'istio_requests.http.503.','istio_requests.grpc.200.14.0','istio_requests.http.200.14.0','istio_requests.grpc.200.9.0','istio_requests.http.200.9.0','istio_requests.grpc.200.13.0','istio_requests.http.200.13.0','istio_requests.grpc.200.2.0','istio_requests.http.302.','istio_requests.http.500.']

    df = pd.DataFrame()
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
                    df = pd.read_csv( file_name  )
                    df = df.sort_values('timestamp') 
                    # print(df)
                    # time.sleep(1)

                    service_list = df['service'].unique()
                    # cmdb_list = df['cmdb_id'].unique()

                    print(service_list)
                    print(len(service_list))
                    # print(cmdb_list)
                    # print(len(cmdb_list))

                    # 每个服务对应一张图，因此循环遍历
                    for single_service in service_list:
                        if single_service in ignore_kpi_lists:
                            continue

                        print(single_service)
                        xdf = df[ df['service'].str.contains( single_service )]
                        # sub_cmdb = xdf['cmdb_id'].unique()

                        # if xdf['value'].max() == 0 and xdf['value'].min() == 0 and xdf['value'].mean() == 0:
                        #     continue

                        # 为便于观察，超过10条的线每次画 10 条
                        plt_dataframe( xdf, 'timestamp', 'value', ['rr','sr','mrt','count'], 'Timestamp', single_service, tdf )

                elif 'kpi_' in file_name:

                    df = pd.read_csv( file_name  )
                    df = df.sort_values('timestamp') 
                    # print(df)
                    # time.sleep(1)

                    kpi_list = df['kpi_name'].unique()
                    cmdb_list = df['cmdb_id'].unique()

                    print(kpi_list)
                    print(len(kpi_list))
                    print(cmdb_list)
                    print(len(cmdb_list))

                    for index, row in tdf.iterrows():

                        for single_cmdb in cmdb_list:
                            print( row['cmdb_id'] + ' , ' + single_cmdb)
                            if row['cmdb_id'] == single_cmdb:
                                xdf = df[ df['cmdb_id'].str.contains(single_cmdb) ]
                                plt_multi_subs(xdf, row)
                            else:
                                continue
                    # # 每个指标对应一张图，因此循环遍历 KPI_LIST
                    # for single_kpi in kpi_list:
                    #     if single_kpi in ignore_kpi_lists:
                    #         continue

                    #     print(single_kpi)
                    #     xdf = df[ df['kpi_name'].str.contains( single_kpi )]
                    #     sub_cmdb = xdf['cmdb_id'].unique()

                    #     if xdf['value'].max() == 0 and xdf['value'].min() == 0 and xdf['value'].mean() == 0:
                    #         continue

                    #     # 为便于观察，超过10条的线每次画 10 条
                    #     plt_dataframe( xdf, 'timestamp', 'value', 'cmdb_id', 'Timestamp', single_kpi, tdf )
                        # if len(sub_cmdb) > 1 and  len(sub_cmdb) > 10:
                        #     pass
                        # elif len(sub_cmdb) > 1 and len(sub_cmdb) <= 10:
                        # else:
                        #     pass

def plt_multi_subs(df, tdf_row, max_sub = 16):
    colors = ['red', 'blue', 'green', 'orange', 'black', 'purple', 'lime', 'magenta', 'cyan', 'maroon', 'teal', 'silver', 'gray', 'navy', 'pink', 'olive', 'rosybrown', 'brown', 'darkred', 'sienna', 'chocolate', 'seagreen', 'indigo', 'crimson', 'plum', 'hotpink', 'lightblue', 'darkcyan', 'gold', 'darkkhaki', 'wheat', 'tan', 'skyblue', 'slategrey', 'blueviolet', 'thistle', 'violet', 'orchid', 'steelblue', 'peru', 'lightgrey']

    x = 0
    y = 0
    max_x = 2
    max_y = 3

    fig, axes = plt.subplots( max_x + 1, max_y + 1, figsize=(16,8))
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['font.sans-serif'] = ['Songti SC']
    plt.rcParams['axes.unicode_minus'] = False


    kpi_lists =  np.sort(df['kpi_name'].unique())
    for signle_kpi in kpi_lists:
        xdf = df[ df['kpi_name'].str.contains(signle_kpi) ]

        #@TODO 去掉零值
        if xdf['value'].mean() == 0 or xdf['value'].std() == 0:
            continue

        if x <= max_x and y <= max_y:
            print( str(x) + ',' + str(y))
            # print(axes)
            ax = axes[x, y]
            ax.plot( xdf['timestamp'], xdf['value'])
            # ax.fill(1647823965, 2, 'red', alpha = 0.3)
            ax.add_patch(patches.Rectangle((tdf_row['timestamp'], xdf['value'].min()), 120, xdf['value'].max(),facecolor="red",alpha=0.5))
            ax.annotate( tdf_row['cmdb_id'] + ',' + tdf_row['failure_type'], xy=( tdf_row['timestamp'],xdf['value'].max()), xytext=(tdf_row['timestamp'] + 200, xdf['value'].max()) )
            ax.set_title(xdf['cmdb_id'].iloc[1] + ':' + signle_kpi)
            y = y + 1

            if y > max_y:
                y = 0
                x = x + 1

            if x > max_x:
                plt.show()
                # print("xxxx")
                fig, axes = plt.subplots(max_x + 1, max_y + 1, figsize=(16,8))
                plt.rcParams["figure.autolayout"] = True
                plt.rcParams['font.sans-serif'] = ['Songti SC']
                plt.rcParams['axes.unicode_minus'] = False
                x = 0

    # plt.show()

# 支持按照文件夹对文件夹内的文件进行画线
def plt_all_metrics(plot_folder = 'node'):
    metric_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/' + plot_folder

    truth_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/groundtruth/groundtruth-k8s-1-2022-03-21.csv'
    tdf = pd.read_csv( truth_file )
    # tdf = tdf[ ~ tdf['level'].str.contains('node')]
    tdf = tdf[ ~ tdf['level'].str.contains('pod')]
    tdf = tdf[ ~ tdf['level'].str.contains('service')]

    # 需要忽略的 KPI
    ignore_kpi_lists = ['istio_requests.grpc.0.2.0', 'istio_requests.grpc.200.0.0', 'istio_requests.grpc.200.4.0', 'istio_requests.http.200.', 'istio_requests.http.202.', 'istio_requests.http.503.','istio_requests.grpc.200.14.0','istio_requests.http.200.14.0','istio_requests.grpc.200.9.0','istio_requests.http.200.9.0','istio_requests.grpc.200.13.0','istio_requests.http.200.13.0','istio_requests.grpc.200.2.0','istio_requests.http.302.','istio_requests.http.500.']

    df = pd.DataFrame()
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
                    df = pd.read_csv( file_name  )
                    df = df.sort_values('timestamp') 
                    # print(df)
                    # time.sleep(1)

                    service_list = df['service'].unique()
                    # cmdb_list = df['cmdb_id'].unique()

                    print(service_list)
                    print(len(service_list))
                    # print(cmdb_list)
                    # print(len(cmdb_list))

                    # 每个服务对应一张图，因此循环遍历
                    for single_service in service_list:
                        if single_service in ignore_kpi_lists:
                            continue

                        print(single_service)
                        xdf = df[ df['service'].str.contains( single_service )]
                        # sub_cmdb = xdf['cmdb_id'].unique()

                        # if xdf['value'].max() == 0 and xdf['value'].min() == 0 and xdf['value'].mean() == 0:
                        #     continue

                        # 为便于观察，超过10条的线每次画 10 条
                        plt_dataframe( xdf, 'timestamp', 'value', ['rr','sr','mrt','count'], 'Timestamp', single_service, tdf )

                elif 'kpi_' in file_name:

                    df = pd.read_csv( file_name  )
                    df = df.sort_values('timestamp') 
                    # print(df)
                    # time.sleep(1)

                    kpi_list = df['kpi_name'].unique()
                    cmdb_list = df['cmdb_id'].unique()

                    print(kpi_list)
                    print(len(kpi_list))
                    print(cmdb_list)
                    print(len(cmdb_list))

                    # 每个指标对应一张图，因此循环遍历 KPI_LIST
                    for single_kpi in kpi_list:
                        if single_kpi in ignore_kpi_lists:
                            continue

                        print(single_kpi)
                        xdf = df[ df['kpi_name'].str.contains( single_kpi )]
                        sub_cmdb = xdf['cmdb_id'].unique()

                        if xdf['value'].max() == 0 and xdf['value'].min() == 0 and xdf['value'].mean() == 0:
                            continue

                        # 为便于观察，超过10条的线每次画 10 条
                        plt_dataframe( xdf, 'timestamp', 'value', 'cmdb_id', 'Timestamp', single_kpi, tdf )
                        # if len(sub_cmdb) > 1 and  len(sub_cmdb) > 10:
                        #     pass
                        # elif len(sub_cmdb) > 1 and len(sub_cmdb) <= 10:
                        # else:
                        #     pass

def plt_dataframe( df, x_column, y_column, s_column, label_x_text, label_y_text, tdf = None ):
    colors = ['red', 'blue', 'green', 'orange', 'black', 'purple', 'lime', 'magenta', 'cyan', 'maroon', 'teal', 'silver', 'gray', 'navy', 'pink', 'olive', 'rosybrown', 'brown', 'darkred', 'sienna', 'chocolate', 'seagreen', 'indigo', 'crimson', 'plum', 'hotpink', 'lightblue', 'darkcyan', 'gold', 'darkkhaki', 'wheat', 'tan', 'skyblue', 'slategrey', 'blueviolet', 'thistle', 'violet', 'orchid', 'steelblue', 'peru', 'lightgrey']

    fig = plt.figure(figsize=(14,8))
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['font.sans-serif'] = ['Songti SC']
    plt.rcParams['axes.unicode_minus'] = False

    # print(df)

    # 1 表示根据列的多个值画线，2 表示按多列画线
    axis_option = 1
    # 根据多个列分别画线
    if type(s_column) is list:
        series_list = s_column
        axis_option = 2
    else:
        # 根据一列中的多个值分别画线
        series_list = df[s_column].unique()
        axis_option = 1

    print(series_list)
    j = 1
    for i in series_list:
        if axis_option == 1:
            cdf = df[ df[s_column].str.contains(i) ]
            # print(cdf)
            # 把 0 值过滤掉
            if cdf['value'].max() == 0 and cdf['value'].min() == 0 and cdf['value'].mean() == 0:
                continue
            plt.plot(cdf[x_column], cdf[y_column], c = colors[ j ], label=i)

            if j < 2:
                # 将故障数据点标注处理啊
                for index, row in tdf.iterrows():
                    plt.plot(row['timestamp'], cdf[y_column].max(), 'o')
                    plt.text(row['timestamp'], cdf[y_column].max(), row['level'] + ',' + row["cmdb_id"] + ',' + row["failure_type"] , ha = 'center', va = 'bottom', fontsize = 8, rotation = 90)

        elif axis_option == 2:
            cdf = df
            plt.plot(cdf[x_column], cdf[i], c = colors[ j ], label=i)

            if j < 2:
                # 将故障数据点标注处理啊
                for index, row in tdf.iterrows():
                    plt.plot(row['timestamp'], cdf[i].max(), 'o')
                    plt.text(row['timestamp'], cdf[i].max(), row['level'] + ',' + row["cmdb_id"] + ',' + row["failure_type"] , ha = 'center', va = 'bottom', fontsize = 8, rotation = 90)


        # print('Plot Line ----' + x_column + ',' + y_column )
        j = j + 1
        if j > 40:
            j = 1


    plt.xlabel( 'X : ' + label_x_text )
    plt.ylabel( label_y_text )
    plt.legend( loc = 'best' )
    plt.show()
        # # if 'disk' in kpi_list[subplot] or '.io.' in kpi_list[subplot]:
        # # if 'cpu' in kpi_list[subplot] or 'load' in kpi_list[subplot]:
        # for x in service_list:
        # # if True:
        #     print(kpi_list[subplot])

        #     xdf = df[ df['cmdb_id'].str.contains(x) ]
        #     fig = plt.figure(figsize=(14,8))
        #     plt.rcParams['font.sans-serif'] = 'Monaco'
        #     # ax = fig.add_subplot(len(kpi_list),1,subplot+1)
        #     bdf = xdf[ xdf['kpi_name'].str.contains(kpi_list[subplot]) ]
        #     # bdf = df[ df['cmdb_id'].str.contains(x) ]

        #     j = 0
        #     # plt.figure()
        #     # for i in cmdb_list:
        #     for i in cmdb_list:
        #         if x in i:
        #             print(i)
        #             cdf = bdf[ bdf['cmdb_id'].str.contains(i)]
        #             print(cdf)
        #             plt.plot(cdf['timestamp'], cdf['value'], c=colors[j], label=i)
        #             j += 1

        #     for i in cloud_error:
        #         plt.plot(i, cdf['value'].max(), 'o')
        #         plt.text(i,cdf['value'].max(),cloud_error[i],ha = 'center',va = 'bottom',fontsize=7,rotation=90)

        #     plt.xlabel('Timestamp')
        #     plt.ylabel(kpi_list[subplot])
        #     plt.legend(loc='best')
        #     plt.show()

# 将 10 份 Metric 数据按照指标绘制到一张图上
# 每种 Kpi 绘制一张图
# 如果 cmdb_id 是 node 级别，所有 node 绘到一张图，不包含点
# 如果 cmdb_id 是 Pod 级别，拆分 service ，根据 service 相同的绘制到一张图，包含点
# 目录结构说明：
def plt_metrics():
    normal_data_prefix = '/Users/shiqiang/Downloads/2022-ccb-aiops/data_normal/'
    faults_data_prefix = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/'

    normal_data_lists = ['cloudbed-1/metric/node/kpi_cloudbed1_metric_0319.csv', 'cloudbed-2/metric/node/kpi_cloudbed2_metric_0319.csv', 'cloudbed-3/metric/node/kpi_cloudbed3_metric_0319.csv']

    faults_data_lists = ['cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv', 'cloudbed-2/metric/node/kpi_cloudbed2_metric_0320.csv', 'cloudbed-3/metric/node/kpi_cloudbed3_metric_0320.csv']

    # 0320 Test File
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/node/kpi_cloudbed1_metric_0320.csv'
    # 0321 Test File
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/node/kpi_cloudbed1_metric_0321.csv'

    # 0321 容器读的指标
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/container/kpi_container_fs_reads.csv'

    # istio 请求指标
    # test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/istio/kpi_istio_requests.csv'

    test_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/cloudbed-1/metric/jvm/kpi_java_lang_OperatingSystem_SystemCpuLoad.csv'

    df = pd.read_csv( test_file )
    
    node_list = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 'node-6']
    colors = ['red', 'blue', 'green', 'orange', 'black', 'purple', 'lime', 'magenta', 'cyan', 'maroon', 'teal', 'silver', 'gray', 'navy', 'pink', 'olive', 'rosybrown', 'brown', 'darkred', 'sienna', 'chocolate', 'seagreen', 'indigo', 'crimson', 'plum', 'hotpink', 'lightblue', 'darkcyan', 'gold', 'darkkhaki', 'wheat', 'tan', 'skyblue', 'slategrey', 'blueviolet', 'thistle', 'violet', 'orchid', 'steelblue', 'peru', 'lightgrey']
    # CPU 故障
    # cloud_error = {1647754788:'node-4,node CPU FAIL', 1647755511: 'node-6,node CPU FAIL', 1647767561:'node-4,node CPU UP'}

    # 0320 磁盘故障
    # cloud_error = {1647749271: 'node-1, disk read io error', 1647753199: 'node-2 disk write io error', 1647769222: 'node-5 disk write io error', 1647776146: 'node-4, disk read io error', 1647784337: 'node-1, disk space error', 1647788164: 'node-3, disk read io error'}

    # 0321 磁盘故障
    # cloud_error = {1647830276: 'node-4, disk space error', 1647852107: 'node-5, disk space error', 1647865567: 'node-3, disk space error', 1647875729: 'node-4, disk space error'}

    # 0321 容器 IO 故障
    cloud_error = { 1647796830: 'productcatalogservice-2 , k8s read io error', 1647818816: 'adservice2-0 , k8s read io error', 1647850299: 'frontend-2 , k8s read io error'}

    truth_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/groundtruth/groundtruth-k8s-1-2022-03-20.csv'
    tdf = pd.read_csv( truth_file )
    tdf = tdf[ ~ tdf['level'].str.contains('node')]
    tdf = tdf[ ~ tdf['level'].str.contains('pod')]

    prev_timestamp = 0
    # print(df.head())
    # time.sleep(100)
    for index, row in df.iterrows():
        # print(row)
        if prev_timestamp == 0:
            prev_timestamp = row['timestamp']
            continue

        if int(row['timestamp']) < prev_timestamp:
            print("Timestamp Error")
            print("index : " + str(index))
            print("timestamp : "  + str(prev_timestamp))
            time.sleep(100)
        else:
            prev_timestamp = index
        
        # print(row["timestamp"])

    # time.sleep(100)
    # print(tdf)

    # print(cloud_error[1647754788])
    # for i in cloud_error:
    #     print(i)

    # print( df['value'].max() )

    kpi_list = df['kpi_name'].unique()
    cmdb_list = df['cmdb_id'].unique()

    # 需要忽略的 KPI
    ignore_kpi_lists = ['istio_requests.grpc.0.2.0', 'istio_requests.grpc.200.0.0', 'istio_requests.grpc.200.4.0', 'istio_requests.http.200.', 'istio_requests.http.202.', 'istio_requests.http.503.','istio_requests.grpc.200.14.0','istio_requests.http.200.14.0','istio_requests.grpc.200.9.0','istio_requests.http.200.9.0','istio_requests.grpc.200.13.0','istio_requests.http.200.13.0','istio_requests.grpc.200.2.0','istio_requests.http.302.','istio_requests.http.500.']


    print(kpi_list)
    # print(df)
    print('-------------------')
    for i in kpi_list:
        if i in ignore_kpi_lists:
            continue

        xdf = df[ df['kpi_name'].str.contains(i) ]

        plt_dataframe( xdf, 'timestamp', 'value', 'cmdb_id', 'timestamp', i , tdf)
        print('===========================')

# 对 Metric 进行统计，思路：
# 加载 groudtruth 数据
# 依次遍历 metric 文件
# 统计数值为 0 的指标并汇总打印列表
# 统计在故障时点 10 分钟内，并且数值大于一天的 90% 的指标，汇总并打印列表。即：对每日指标数据求最大值，如时间戳与故障点时间戳之差在 10 分钟内，即打印。
# 统计在故障点 10 分钟内，故障点后 5 个数值在每日样本中的排名
def metric_stat():
    metric_folder = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/tar/20220321/cloudbed-1/metric/'

    truth_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/training_data_with_faults/groundtruth/groundtruth-k8s-1-2022-03-21.csv'
    tdf = pd.read_csv( truth_file )
    # tdf = tdf[ ~ tdf['level'].str.contains('node')]
    # tdf = tdf[ ~ tdf['level'].str.contains('pod')]

    ignore_kpi_lists = ['istio_tcp_sent_bytes.UF,URX', 'istio_request_duration_milliseconds.grpc.200.2.0', 'istio_requests.grpc.200.2.0', 'istio_agent_pilot_conflict_outbound_listener_http_over_current_tcp', 'istio_agent_go_memstats_lookups', 'istio_agent_pilot_vservice_dup_domain', 'istio_agent_wasm_cache_entries', 'istio_tcp_connections_opened.UF,URX', 'istio_tcp_connections_closed.UF,URX', 'istio_agent_pilot_eds_no_instances', 'istio_request_bytes.grpc.200.2.0', 'istio_response_bytes.grpc.0.2.0', 'istio_response_bytes.grpc.200.2.0', 'istio_response_bytes.http.0.', 'istio_agent_pilot_conflict_outbound_listener_tcp_over_current_http', 'istio_tcp_received_bytes.UF,URX', 'istio_agent_pilot_conflict_outbound_listener_tcp_over_current_tcp', 'istio_agent_pilot_endpoint_not_ready', 'istio_agent_pilot_conflict_inbound_listener', 'istio_agent_endpoint_no_pod', 'istio_agent_pilot_no_ip', 'istio_agent_pilot_duplicate_envoy_clusters', 'istio_agent_pilot_virt_services', 'istio_agent_pilot_destrule_subsets', 'java_nio_BufferPool_TotalCapacity.mapped', 'jvm_threads_deadlocked_monitor', 'java_lang_MemoryPool_CollectionUsageThresholdSupported.Metaspace', 'java_lang_MemoryPool_CollectionUsageThresholdSupported.Compressed_Class_Space', 'java_lang_MemoryPool_CollectionUsageThresholdSupported.Code_Cache', 'jvm_buffer_pool_used_buffers.mapped', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_init.Metaspace.MarkSweepCompact', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_init.Metaspace.Copy', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_init.Compressed_Class_Space.MarkSweepCompact', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_init.Compressed_Class_Space.Copy', 'java_lang_MemoryPool_UsageThreshold.Compressed_Class_Space', 'java_lang_MemoryPool_UsageThreshold.Metaspace', 'java_lang_MemoryPool_UsageThreshold.Code_Cache', 'java_lang_MemoryPool_UsageThreshold.Tenured_Gen', 'java_lang_MemoryPool_Usage_init.Metaspace', 'java_lang_MemoryPool_Usage_init.Compressed_Class_Space', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageBeforeGc_init.Compressed_Class_Space.Copy', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageBeforeGc_init.Metaspace.Copy', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageBeforeGc_init.Metaspace.MarkSweepCompact', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageBeforeGc_init.Compressed_Class_Space.MarkSweepCompact', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageBeforeGc_used.Eden_Space.MarkSweepCompact', 'java_lang_OperatingSystem_FreeSwapSpaceSize', 'jvm_threads_deadlocked', 'jvm_buffer_pool_capacity_MB.mapped', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_used.Survivor_Space.MarkSweepCompact', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_used.Eden_Space.Copy', 'java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_used.Eden_Space.MarkSweepCompact', 'jvm_memory_pool_MB_init.Metaspace', 'jvm_memory_pool_MB_init.Compressed_Class_Space', 'java_lang_MemoryPool_CollectionUsageThresholdExceeded.Eden_Space', 'java_lang_MemoryPool_CollectionUsageThresholdExceeded.Survivor_Space', 'java_lang_MemoryPool_CollectionUsageThresholdExceeded.Tenured_Gen', 'java_lang_MemoryPool_CollectionUsage_used.Eden_Space', 'jvm_buffer_pool_used_MB.mapped', 'java_nio_BufferPool_Count.mapped', 'java_lang_MemoryPool_CollectionUsageThreshold.Eden_Space', 'java_lang_MemoryPool_CollectionUsageThreshold.Survivor_Space', 'java_lang_MemoryPool_CollectionUsageThreshold.Tenured_Gen', 'java_lang_Memory_Verbose', 'java_lang_ClassLoading_Verbose', 'jvm_threads_state.BLOCKED', 'jvm_threads_state.NEW', 'jvm_threads_state.TERMINATED', 'java_lang_Threading_ThreadContentionMonitoringEnabled', 'java_lang_MemoryPool_UsageThresholdSupported.Eden_Space', 'java_lang_MemoryPool_UsageThresholdSupported.Survivor_Space', 'java_nio_BufferPool_MemoryUsed.mapped', 'java_lang_MemoryPool_UsageThresholdCount.Code_Cache', 'java_lang_MemoryPool_UsageThresholdCount.Compressed_Class_Space', 'java_lang_MemoryPool_UsageThresholdCount.Metaspace', 'java_lang_MemoryPool_UsageThresholdCount.Tenured_Gen', 'java_lang_MemoryPool_CollectionUsageThresholdCount.Eden_Space', 'java_lang_MemoryPool_CollectionUsageThresholdCount.Tenured_Gen', 'java_lang_MemoryPool_CollectionUsageThresholdCount.Survivor_Space', 'java_lang_OperatingSystem_TotalSwapSpaceSize', 'java_lang_MemoryPool_PeakUsage_init.Metaspace', 'java_lang_MemoryPool_PeakUsage_init.Compressed_Class_Space', 'java_lang_MemoryPool_UsageThresholdExceeded.Code_Cache', 'java_lang_MemoryPool_UsageThresholdExceeded.Tenured_Gen', 'java_lang_MemoryPool_UsageThresholdExceeded.Metaspace', 'java_lang_MemoryPool_UsageThresholdExceeded.Compressed_Class_Space', 'container_network_transmit_packets_dropped.eth0', 'container_network_receive_errors.eth0', 'container_fs_writes_merged./dev/vda1', 'container_threads_max', 'container_fs_write_seconds./dev/vda1', 'container_fs_inodes_free./dev/vda1', 'container_fs_sector_reads./dev/vda1', 'container_fs_reads./dev/vda1', 'container_fs_io_time_weighted_seconds./dev/vda1', 'container_fs_sector_writes./dev/vda1', 'container_fs_io_current./dev/vda1', 'container_fs_io_time_seconds./dev/vda1', 'container_fs_writes./dev/vda1', 'container_tasks_state.iowaiting', 'container_tasks_state.running', 'container_tasks_state.uninterruptible', 'container_tasks_state.sleeping', 'container_tasks_state.stopped', 'container_fs_read_seconds./dev/vda1', 'container_spec_memory_reservation_limit_MB', 'container_memory_swap', 'container_network_transmit_errors.eth0', 'container_fs_reads_merged./dev/vda1', 'container_cpu_load_average_10s', 'system.net.udp.snd_buf_errors', 'system.swap.used_pct', 'system.net.udp.rcv_buf_errors', 'system.net.packets_out.error', 'system.swap.free', 'system.swap.total', 'system.swap.used', 'system.disk.readonly', 'system.swap.so', 'system.swap.si']

    ignore_equal_lists = []

    # 0值 119，非0值 462
    zero_kpi_list = []
    equal_kpi_list = []
    nonzero_kpi_list = []
    nonzero_union_list = []
    # { kpi_name : '', file_name : '', max_value : '', error_timestamp : '', max_value_timestamp : '' }
    max_value_kpi_list = {}
    # { }
    error_value_pct = {}


    df = pd.DataFrame()
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
                    df = pd.read_csv( file_name  )
                    df = df.sort_values('timestamp') 
                elif 'kpi_' in file_name:
                    df = pd.read_csv( file_name  )
                    df = df.sort_values('timestamp') 

                    kpi_list = df['kpi_name'].unique()
                    cmdb_list = df['cmdb_id'].unique()

                    # 每个指标对应一张图，因此循环遍历 KPI_LIST
                    for single_kpi in kpi_list:
                        if single_kpi in ignore_kpi_lists:
                            continue

                        xdf = df[ df['kpi_name'].str.contains( single_kpi )]

                        if xdf['value'].max() == 0 and xdf['value'].min() == 0 and xdf['value'].mean() == 0:
                            zero_kpi_list.append( single_kpi )
                        else:
                            # 如果每个 cmdb_id 对应的 kpi 值也是一条直线，则也忽略
                            for single_cmdb in cmdb_list:
                                if single_cmdb+':'+single_kpi in ignore_equal_lists:
                                    continue

                                zdf = xdf[ xdf['cmdb_id'].str.contains( single_cmdb ) ]

                                if zdf.empty:
                                    continue

                                if zdf['value'].max() == zdf['value'].min() and zdf['value'].std() == 0:
                                    if single_cmdb + ':' + single_kpi not in equal_kpi_list:
                                        equal_kpi_list.append( single_cmdb + ':' + single_kpi)
                                else:
                                    if single_kpi not in nonzero_kpi_list:
                                        nonzero_kpi_list.append(single_kpi)

                                    if single_cmdb + ':' + single_kpi not in nonzero_union_list:
                                        nonzero_union_list.append( single_cmdb + ':' + single_kpi )

                                    for index, row in tdf.iterrows():
                                        if abs(row['timestamp'] - df.iloc[ zdf['value'].idxmax() + 1 ]['timestamp']) < 10:
                                            print( single_cmdb + ':' + single_kpi + ': max = ' + str(zdf['value'].max() ) + ', row index = ' + str(zdf['value'].idxmax() ) + ', timestamp = ' + str(df.iloc[ zdf['value'].idxmax() + 1 ]['timestamp']) )
                                            print(row)
                                            max_value_kpi_list[single_cmdb + ':' + single_kpi] = { 'cmdb_id' : single_cmdb, 'kpi_name' : single_kpi, 'max_value' : zdf['value'].max(), 'timestamp' : str(df.iloc[ zdf['value'].idxmax() + 1 ]['timestamp']) ,'error_timestamp' : str(row['timestamp']), 'level' : row['level'],  'error_cmdb_id' : row['cmdb_id'], 'failure_type' : row['failure_type'] }

    print('len(equal_kpi_list) = ' + str(len(equal_kpi_list)))
    print('len(nonzero_kpi_list) = ' +  str(len(nonzero_kpi_list)))
    print('len(nonzero_union_list) = ' +  str(len(nonzero_union_list)))
    print(max_value_kpi_list)

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "m:h:f:", ["mode", "help", "folder"])

    for o, a in opts:
        if o in ("-h", "--help"):
            print("Usage: python3 moyu.py -m method")
        if o in ("-m", "--method"):
            PROCESS_METHOD = a
        if o in ("-f", "--folder"):
            PLOT_FOLDER = 'node'

    if PROCESS_METHOD == 'plotall':
        plt_all_metrics(PLOT_FOLDER)
    elif PROCESS_METHOD == 'plotsingle':
        # 对比 Metric 并绘图
        plt_metrics()
    elif PROCESS_METHOD == 'stat':
        # 统计分析 metric 数据
        metric_stat()
    elif PROCESS_METHOD == 'plotsub':
        error_plt(PLOT_FOLDER)


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