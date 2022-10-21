import os
import pandas as pd
from sklearn.model_selection import train_test_split
# from sklearn import train_test_split

# 《Python金融大数据风控建模实战》书本内容代码

def data_read(data_path, file_name):
    # df = pd.read_csv(os.path.join(data_path, file_name), delim_whitespace= True, header = None, sep=',')
    # 原书中代码为上面一行，因为我找到的数据集是逗号分隔，修改为下面
    df = pd.read_csv(os.path.join(data_path, file_name),  header = None, sep=',')
    columns = ['status_account', 'duration', 'credit_history', 'purpose', 'amount', 'svaing_account', 'present_emp', 'income_rate', 'personal_status', 'other_debtors', 'residence_info', 'property', 'age', 'inst_plans', 'housing', 'num_credits', 'job', 'dependents', 'telephone', 'foreign_worker', 'target']

    df.columns = columns
    df.target = df.target - 1
    data_train, data_test = train_test_split(df, test_size=0.2, random_state=0, stratify=df.target)
    
    return data_train, data_test

data_path = '/Users/shiqiang/Projects/sh-valley/python/risk_control/datasets'
file_name = 'GermanData.csv'

data_train, data_test = data_read(data_path, file_name)

print(data_train)
print(data_test)