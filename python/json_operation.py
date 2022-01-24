#encoding = utf-8
import json
import re

# 处理学习记录
filePath = 'score1.json'

total_time = 0
with open(filePath, 'r', encoding='utf-8') as file:
    data = json.load(file)
    # print(json.loads(filePath))
    for i in data['data']:
        # print(i)
        # 查找字符串中的数字
        nums = re.findall('(\d+\.\d+)', i['remark'])
        print(nums[0])
        total_time = total_time + float(nums[0])
        # print(i['remark'])

print(total_time)


# 处理考勤记录
# filePath = 'mobile.json'

# with open(filePath, 'r', encoding='utf-8') as file:
#     data = json.load(file)
#     # print(json.loads(filePath))
#     for i in data:
#         # print(i['code'])
#         if( i['data']['total'] > 0):
#             for j in i['data']['list']:
#                 print("{} {} {:60s} {} {}".format(j['usrNm'], j['deviceId'], j['deviceName'], j['bondedTime'], j['bondedStatus']))
#         # print(i)
#         # print('-----------')
#     # print(data)