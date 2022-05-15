from kafka import KafkaConsumer
import time, json, requests, os, random, sys, getopt, datetime, re
import pandas as pd
from pandas import DataFrame, DatetimeIndex

# 框架思路
# 1. 按时间戳分批次读取原始指标数据
# 2. 区分指标，经过训练时间段后，开始进行异常数据的判断，将发现的异常数据压入队列
# 3. 每个时间批次结束后，汇总指标异常的情况，判断是否有故障发生