import requests
import json
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor
from douguo_mongo import mongo_info

queue_list = Queue()

def douguo_request(url, data):
    headers = {
        "client":"4",
        "version":"6962.2",
        "device":"SM-N960F",
        "sdk":"22,5.1.1",
        "channel":"baidu",
        "resolution":"1600*900",
        "display-resolution":"1600*900",
        "dpi":"2.0",
        "brand":"samsung",
        "scale":"2.0",
        "timezone":"28800",
        "language":"zh",
        "cns":"2",
        "carrier":"CMCC",
        "imsi":"460072922802166",
        "User-Agent":"Mozilla/5.0 (Linux; Android 5.1.1; SM-N960F Build/JLS36C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36",
        "uuid":"9690d300-a56a-41c0-bb14-aa4bcbe0e50b",
        "battery-level":"0.59",
        "battery-state":"2",
        "terms-accepted":"1",
        "newbie":"1",
        "reach":"10000",
        "act-code":"1590130934",
        "act-timestamp":"1590130934",
        "Content-Type":"application/x-www-form-urlencoded; charset=utf-8",
        "Accept-Encoding":"gzip, deflate",
        "Connection":"Keep-Alive",
        "Host":"api.douguo.net",
    }

    r = requests.post(url=url, data=data, headers=headers)
    return r


def douguo_index():
    url = 'http://api.douguo.net/recipe/flatcatalogs'
    data = {
        "client":"4",
        #"_session" : "1568947372977863254011601605",
        #"v" : "1568891837",
        "_vs" : "2305"
    }

    r = douguo_request(url,data)
    # 需要把json数据变为dict
    response_dict = json.loads(r.text)
    for item1 in response_dict['result']['cs']:
        for item2 in item1['cs']:
            for item3 in item2['cs']:
                data = {
                    'client':'4',
                    'keyword':item3['name'],
                    '_vs':'400'
                }
                # return data
                # 放入队列使用put方法
                queue_list.put(data)

def douguo_item(data):
    item_index_number = 0
    print('当前处理食材', data['keyword'])
    url = 'http://api.douguo.net/search/universalnew/0/10'
    r = douguo_request(url=url,data=data)
    list_response_dict = json.loads(r.text)
    for item in list_response_dict['result']['recipe']['recipes']:
        item_index_number += 1
        info = {}
        info['shicai'] = data['keyword']
        info['author'] = item['an']
        info['shicai_id'] = item['id']
        info['shicai_name'] = item['n']
        info['describe'] = item['cookstory']
        info['cailiao_list'] = item['major']
        detail_url = 'http://api.douguo.net/recipe/detail/' + str(info['shicai_id'])
        detail_data = {
            "client": "4",
            "_session": "15900498035869ae88598e4c49bf1",
            "author_id": "0",
            "_vs": "11101",
            "_ext": '{"query":{"kw":'+str(info['shicai'])+',"src":"11101","idx":'+str(item_index_number)+',"type":"13","id":'+str(info['shicai_id'])+'}}'
        }
        detail_response = douguo_request(url=detail_url,data=detail_data)
        detail_response_dict = json.loads(detail_response.text)
        info['tips'] = detail_response_dict['result']['recipe']['tips']
        info['cook_step'] = detail_response_dict['result']['recipe']['cookstep']
        print('当前处理的菜谱是：', info['shicai_name'])
        mongo_info.insert_item(info)


douguo_index()
# 同时进行的任务数
pool = ThreadPoolExecutor(max_workers=25)
while(queue_list.qsize()>0):
    pool.submit(douguo_item,queue_list.get())
