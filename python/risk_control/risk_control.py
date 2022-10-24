import os
import pandas as pd
# import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
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

def onehot_encode( df, data_path_1, flag = 'train'):
    df = df.reset_index(drop=True)

    # 判断数据集是否存在缺失值
    if sum(df.isnull().any()) > 0:
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        var_numerics = df.select_dtypes(include=numerics).columns
        var_str = [i for i in dfcolumns if i not in var_numerics]

        # 数据类型的缺失值用 -77777 填补
        if len(var_numerics) > 0:
            df.loc[:,var_numerics] = df[var_numerics].fillna(-7777)

        # 字符类型的缺失值用 NA 填补
        if len(var_str) > 0:
            df.loc[:,var_str] = df[var_str].fillna('NA')

        if flag == 'train':
            # 由训练集得到编码规则
            enc = OneHotEncoder().fit(df)

            # 保存编码规则
            save_model = open(os.path.join(data_path_1, 'onehot.pkl'), 'wb')
            pickle.dump(enc, save_model, 0)
            save_model.close()

data_path = '/Users/shiqiang/Projects/sh-valley/python/risk_control/datasets'
file_name = 'GermanData.csv'

data_train, data_test = data_read(data_path, file_name)

print(data_train)
print(data_test)