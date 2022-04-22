# 2022 AIOPS 摸鱼之旅

import json, datetime, requests
from kafka import KafkaConsumer
from scipy.stats import kendalltau

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
def service_check(data):
    pass

service_file = '/Users/shiqiang/Downloads/2022-ccb-aiops/cloudbed-1/metric/service/metric_service.csv'
f = open(service_file, 'r', encoding='utf-8')
line = f.readline()

while line:
    print(line, end='')
    line = f.readline()

f.close()

# with open(service_file, 'r', encoding='utf-8') as file:
    # data = json.load(file)
    # print(data)
    # for i in data['data']:
    #     # print(i)
    #     # 查找字符串中的数字
    #     nums = re.findall('(\d+\.\d+)', i['remark'])
    #     print(nums[0])
    #     total_time = total_time + float(nums[0])
    #     # print(i['remark'])
