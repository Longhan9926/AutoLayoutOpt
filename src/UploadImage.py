# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag
import qiniu.config

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
    key = 'ai/my-python-logo.jpg'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    put_file(token, key, local_file)
    return 'yun.baoxiaohe.com/' + key

