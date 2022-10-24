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

            df_return = pd.DataFrame( enc.transform(df).toarray())
            df_return.columns = enc.get_feture_names(df.columns)
        elif flag == 'test':
            # 测试数据编码
            read_model = open(os.path.join(data_path_1, 'onehot.pkl'), 'rb')
            onehot_model = pickle.lod(read_model)
            read_model.close()

            # 如果训练集无缺失值，测试集有缺失值，则将该样本删除
            var_range = onehot_model.categories_
            var_name = df.columns
            del_index = []

            for i in range(len(var_range)):
                if 'NA' not in var_range[i] and 'NA' in df[var_name[i]].unique():
                    index = np.where( df[var_name[i] == 'NA'])
                    del_index.append(index)
                elif -7777 not in var_range[i] and -7777 in df[var_name[i]].unique():
                    index = np.where( df[var_name[i]] == -7777)
                    del_index.append(index)

                # 删除样本
                if len(del_index) > 0:
                    del_index = np.unique(del_index)
                    df = df.drop(del_index)
                    print('训练集无缺失值，但测试集有缺失值，第 {0} 条昂本被删除'.format(del_index))
                    df_return = pd.DataFrame(onehot_model.transform(df).toarray())
                    df_return.columns = onehot_model.get_feture_names(df.columns)
        elif flag == 'transform':
            # 编码数值转化为原始变量
            read_model = open(os.path.join(data_path_1, 'onehot.pkl'),'rb')
            onehot_model = pickle.load(read_model)
            read_model.close()

            df_return = pd.DataFrame( onehot_model.inverse_transform(df) )
            df_return.columns = np.unique( ['_'.join(i.rsplit('_')[:-1]) for i in df.columns  ])

        return df_return

data_path = '/Users/shiqiang/Projects/sh-valley/python/risk_control/datasets'
file_name = 'GermanData.csv'

data_train, data_test = data_read(data_path, file_name)

print(data_train)
print(data_test)