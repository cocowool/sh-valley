#encoding = utf-8

# 测试单指标异常检测算法

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


file_path = '/Users/shiqiang/Downloads/2022-ccb-aiops/cloudbed-1/metric/service/metric_service.csv'

appmon = pd.read_csv(file_path)
# appmon.head()

# plt.figure()
# plt.scatter(appmon['sr'], appmon['mrt'])
# plt.show()

# 计算每个指标的平均值
total_num = len(appmon)
average = np.sum(appmon, axis=0)
mu = average / total_num
mu