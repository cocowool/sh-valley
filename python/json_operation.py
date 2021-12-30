#encoding = utf-8
import json

filePath = 'mobile.json'

with open(filePath, 'r', encoding='utf-8') as file:
    data = json.load(file)
    # print(json.loads(filePath))
    for i in data:
        # print(i['code'])
        if( i['data']['total'] > 0):
            for j in i['data']['list']:
                print("{} {} {:60s} {} {}".format(j['usrNm'], j['deviceId'], j['deviceName'], j['bondedTime'], j['bondedStatus']))
        # print(i)
        # print('-----------')
    # print(data)