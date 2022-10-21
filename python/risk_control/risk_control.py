import os
import pandas as pd

# 《Python金融大数据风控建模实战》书本内容代码

def data_read(data_path, file_name):
    df = pd.read_csv(os.path.join(data_path, file_name), delim_whitespace= True, header = None)
    columns = ['status_account', 'duration', 'credit_history', 'purpose', 'amount', 'svaing_account', 'present_emp', 'income_rate', 'personal_status', 'other_debtors', 'residence_info', 'property', 'age', 'inst_plans', 'housing', 'num_credits', 'job', 'dependents', 'telephone', 'foreign_worker', 'target']

    # df.columns = columns
    df.target = df.target - 1
    data_train, data_test = train_test_split(df, test_size=0.2, random_state=0, stratify=df.target)
    
    return data_train, data_test

data_path = '/Users/shiqiang/Projects/opensource-project/credit-risk-workshop-cpd/data/original'
file_name = 'german_credit_data.csv'
data_read(data_path, file_name)