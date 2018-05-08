#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# @Time   : 2017/3/28 8:46
# @Author : Lyrichu
# @Email  : 919987476@qq.com
# @File   : NetCloud_spider3.py
'''
@Description:
网易云音乐评论爬虫，可以完整爬取整个评论
部分参考了@平胸小仙女的文章(地址:https://www.zhihu.com/question/36081767)
post加密部分也给出了，可以参考原帖：
作者：平胸小仙女
链接：https://www.zhihu.com/question/36081767/answer/140287795
来源：知乎
'''
from Crypto.Cipher import AES
import base64
import requests
import json
import codecs
import time
from concurrent.futures import ThreadPoolExecutor

# 头部信息
headers = {
    'Host': "music.163.com",
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)' +
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8",
    'Accept-Encoding': "gzip, deflate",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cookie': "_ntes_nnid=b316fe2686a3a0877a7d853e79abc2ea,1525767520447;\
    _ntes_nuid=b316fe2686a3a0877a7d853e79abc2ea; Province=020; City=0755;\
    vjuids=-17e083ea.1633f115b3b.0.e770523537072;vjlast=1525771492.152577\
    1492.30;NNSSPID=394e68813b96410b94d2ec19de9c8e16; NTES_hp_textlink1=o\
    ld;JSESSIONID-WYYY=U5eU8w8koPlgFAlIeanAH4W%2BBb9R34DKyN0TR3F7%5C5BAJa\
    K9mzHlrvempw234BsepKysPMS7%5CrzBzuJRADlQ7DU2vd5eS6GN6MzUEgKfOAmshXweU\
    rcOVkbjkib7ReNe46ectWVaJp7e4sdOc6vKYIv7SmUKlSd%2B66vlOycI4OSV3Rz%5C%3\
    A1525773308317; _iuqxldmzr_=32; WM_TID=dHu1ag4T7i3c9lwxTLdG5rTUj4668Q\
    lS; __utma=94650624.1525982280.1525767521.1525767521.1525771509.2; __\
    utmb=94650624.4.10.1525771509; __utmc=94650624; __utmz=94650624.15257\
    67521.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    'Connection': "keep-alive",
    'Referer': 'http: //music.163.com/'
}
# 设置代理服务器
proxies = {
    'http:': 'http://121.232.146.184',
    'https:': 'https://144.255.48.197'
}

# offset的取值为:(评论页数-1)*20,total第一页为true，其余页为false
# first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
# 第一个参数
second_param = "010001"  # 第二个参数
# 第三个参数
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615b\
b7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecb\
da92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d\
3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
# 第四个参数
forth_param = "0CoJUm6Qyw8W8jud"


# 获取Post参数params
def get_params(page):  # page为传入页数
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    if(page == 1):  # 如果为第一页
        first_param = '{rid:"", offset:"0", total:"true",\
 limit:"20", csrf_token:""}'
        h_encText = AES_encrypt(first_param, first_key, iv)
    else:
        offset = str((page-1)*20)
        first_param = '{rid:"", offset:"%s", total:"%s", \
limit:"20", csrf_token:""}' % (offset, 'false')
        h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText


# 获取Post参数 encSecKey
def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff\
9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d51\
2f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3\
f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey


# 解密过程
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


def get_json(url, params):
    data = {
         "params": params,
         "encSecKey": get_encSecKey()
    }
    response = requests.post(url, headers=headers, data=data, proxies=proxies)
    return response.content


# 获得评论json数据
def get_comment(url, params):
    data = {
         "params": params,
         "encSecKey": get_encSecKey()
    }
    response = requests.post(url, headers=headers, data=data, proxies=proxies)
    json_dict = json.loads(response.content)
    comments = []
    for item in json_dict['comments']:
        comment = item['content']  # 评论内容
        likedCount = item['likedCount']  # 点赞总数
        comment_time = item['time']  # 评论时间(时间戳)
        userID = item['user']['userId']  # 评论者id
        nickname = item['user']['nickname']  # 昵称
        avatarUrl = item['user']['avatarUrl']  # 头像地址
        comment_info = unicode(userID) + u" " + nickname + u" " + avatarUrl + \
            u" " + unicode(comment_time) + u" " + unicode(likedCount) +  \
            u" " + comment + u"\n"
        comments.append(comment_info)
    return comments


def get_all_comments(url):  # 多线程爬取
    all_comments_list = []  # 存放所有评论
    all_comments_list.append(
        u"用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n")  # 头部信息
    params = get_params(1)
    json_text = get_json(url, params)
    json_dict = json.loads(json_text)
    comments_num = int(json_dict['total'])
    if(comments_num % 20 == 0):
        page = comments_num / 20
    else:
        page = int(comments_num / 20) + 1
    print("共有%d页评论!" % page)
    all_params = []
    urls = []
    for i in range(page):  # 逐页抓取
        params = get_params(i+1)
        all_params.append(params)
        urls.append(url)
    all_comments_list = []
    with ThreadPoolExecutor(40) as executor:
        result = executor.map(get_comment, urls, all_params)
    for r in result:
        all_comments_list.extend(r)
    return all_comments_list


# 将评论写入文本文件
def save_to_file(comment_list, filename):
        with codecs.open(filename, 'a', encoding='utf-8') as f:
            f.writelines(comment_list)
        print("写入文件成功!")


if __name__ == "__main__":
    start_time = time.time()  # 开始时间
    url = "http://music.163.com/weapi/v1/\
resource/comments/R_SO_4_448184048/?csrf_token="
    filename = u"炜炜一笑.txt"
    all_comments_list = get_all_comments(url)
    save_to_file(all_comments_list, filename)
    end_time = time.time()  # 结束时间
    print("程序耗时%f秒." % (end_time - start_time))