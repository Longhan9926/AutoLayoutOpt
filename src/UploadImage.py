# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag
from .RandomG import random_name
import requests
import json

# 需要填写你的 Access Key 和 Secret Key
access_key = "aLCkmgivwb8OWtI9B48FUpNFQR2Yg3gtqkp04d8v"
secret_key = "xjTVdwi1ADJMFSQRAYWGCi84d04_m0QyS47n4-GP"
# 构建鉴权对象
q = Auth(access_key, secret_key)
# 要上传的空间
bucket_name = "bxh"


# bucket_host = "//cloud.baoxiaohe.com/"


def upload_image(local_file):
    # 上传后保存的文件名
    name = random_name(1)
    key = 'ai/' + name + '.png'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    put_file(token, key, local_file)
    return '//yun.baoxiaohe.com/' + key


def http_put(values):
    url = 'https://www.baoxiaohe.com/api/v2/projects'

    payload = json.dumps(values).encode('UTF-8')

    headers = {
        'authentication': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NzA3NiwidHlwZSI6InVzZXIiLCJpc19hZG1pbiI6MCwiaWF0IjoxNjExODI3NTk3LCJleHAiOjE2MTI0MzIzOTd9.Reb2G_WoODIrkZpxlE51g9kcrj5Dp5ctu6oZml2mPrU',
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)


if __name__ == '__main__':
    with open('../design.json', 'r') as load_f:
        design = json.load(load_f)
    with open('../upload_raw.json', 'r') as f:
        collection = json.load(f)
        collection["design_data"] = json.dumps(design)
    http_put(collection)