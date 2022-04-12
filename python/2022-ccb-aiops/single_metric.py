#encoding = utf-8

# 测试单指标异常检测算法

import pandas as pd
import numpy as np

file_path = '/Users/shiqiang/Downloads/2022-ccb-aiops/cloudbed-1/metric/service/metric_service.csv'

appmon = pd.read_csv(file_path)