# -*- coding: utf-8 -*-
# @AuThor  : frank_lee
import requests
import json
from multiprocessing import Queue
from handle_mongo import save_to_mongo
from concurrent.futures import ThreadPoolExecutor  # 多线程
queue_list = Queue()


def handle_request(url, data):
    headers = {
        "client": "4",
        "version": "6935.2",
        "device": "OPPO R11",
        "sdk": "22,5.1.1",
        "imei": "866174010201065",
        "channel": "baidu",
        "resolution": "720*1280",
        "dpi": "1.5",
        "brand": "OPPO",
        "scale": "1.5",
        "timezone": "28800",
        "language": "zh",
        "cns": "3",
        "carrier": "CHINA+MOBILE",
        "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; OPPO R11 Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36",
        "reach": "1",
        "newbie": "0",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Host": "api.douguo.net",
        "Content-Length": "89",
    }
    response = requests.post(url=url, headers=headers, data=data)
    return response


def handle_index():
    url = "http://api.douguo.net/recipe/flatcatalogs"
    data = {
        "client": "4",
        "_vs": "2305",
    }
    response = handle_request(url=url, data=data)
    index_data = json.loads(response.text)
    for cate_meishi in index_data['result']['cs']:
        for second_cate_meishi in cate_meishi['cs']:
            for third_cate_meishi in second_cate_meishi['cs']:
                data_2 = {
                    "client": "4",
                    "keyword": third_cate_meishi['name'],
                    "order": "3",
                    "_vs": "400",
                }
                queue_list.put(data_2)


def handle_caipu_list(data):
    caipu_list_url = "http://api.douguo.net/recipe/v2/search/0/20"
    caipu_list_response = handle_request(caipu_list_url, data)
    caipu_list_dict = json.loads(caipu_list_response.text)
    for item in caipu_list_dict['result']['list']:
        caipu_info = {}
        caipu_info['shicai'] = data['keyword']
        if item['type'] == 13:
            caipu_info['user_name'] = item['r']['an']
            caipu_info['dish_name'] = item['r']['n']
            caipu_info['dish_id'] = item['r']['id']
            caipu_info['nandu_xishu'] = item['r']['cook_difficulty']
            caipu_info['cook_time'] = item['r']['cook_time']
            caipu_info['cailiao'] = item['r']['major']
            detail_url = "http://api.douguo.net/recipe/detail/"+str(caipu_info['dish_id'])
            detail_data = {
                "client": "4",
                "author_id": "0",
                "_vs": "2803",
                "_ext": '{"query":{"kw":'+data['keyword']+',"src":"2803","idx":"2","type":"13","id":'+str(item['r']['fc'])+'"}}',
            }
            detail_response = handle_request(detail_url, detail_data)
            detail_response_dict = json.loads(detail_response.text)

            if not isinstance(detail_response_dict['result'], str):
                caipu_info['tips'] = detail_response_dict['result']['recipe']['tips']
                caipu_info['cookstep'] = detail_response_dict['result']['recipe']['cookstep']
                print("当前入库的是", caipu_info['dish_name'])
                save_to_mongo.insert_to_mongo(caipu_info)
            else:
                continue

        else:
            continue


handle_index()
pool = ThreadPoolExecutor(max_workers=20)
while queue_list.qsize() > 0:
    pool.submit(handle_caipu_list, queue_list.get())


