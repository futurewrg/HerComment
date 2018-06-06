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
import logging
from concurrent.futures import ThreadPoolExecutor
from proxy import get_proxy
from proxy import change_proxy
from proxy import get_ua

# 头部信息
headers = {
    'Host': "music.163.com",
    'User-Agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
    'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8",
    'Accept-Encoding': "gzip, deflate",
    'Content-Type': "application/x-www-form-urlencoded",
    'Connection': "keep-alive",
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


# 获取playlist的参数
def get_params_songs(listId):
    first_param = '{id: "%s", ids: "[%s]",\
 limit: 10000, offset: 0, csrf_token: ""}' % (listId, listId)
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText


# 获取user的playlist参数
def get_params_playlist(userId):
    first_param = '{limit:"36", offset:"0",\
total:"true", uid:"%s", wordwrap: "7", csrf_token:""}' % (userId)
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText


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
#    proxy = get_proxy()
    headers['User-Agent'] = get_ua()
    response = requests.post(url, headers=headers,
                             data=data)   # , proxies={'http:': proxy})
    content = json.loads(response.content)
    while True:
        if 'code' in content and 'msg' in content:
            try:
                if content['code'] == -460 and content['msg'] == 'Cheating':
                    #                    proxy = change_proxy(proxy)
                    headers['User-Agent'] = get_ua()
                    response = requests.post(url, headers=headers,
                                        data=data)
                    content = json.loads(response.content)
            except Exception, e:
                print e
                print type(content)
                print type(response.content)

        else:
            break
    return content


# def get_html(url):
#     response = requests.get(url)
#     return response.content


# 获得评论json数据
def get_comment(url, params):
    json_dict = get_json(url, params)
    comments = []
    for item in json_dict['comments']:
        comment = {'comment': item['content'], 'comment_time': item['time'],
                   'userID': item['user']['userId'],
                   'nickname': item['user']['nickname']}
        comments.append(comment)
    return comments


def get_all_comments(songId):  # 多线程爬取
    url = "http://music.163.com/weapi/v1/\
resource/comments/R_SO_4_" + unicode(songId) + "/?csrf_token="
    all_comments_list = []  # 存放所有评论
    all_comments_list.append(
        u"用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n")  # 头部信息
    params = get_params(1)
    json_dict = get_json(url, params)
    if 'total' in json_dict:
        comments_num = int(json_dict['total'])
    else:
        comments_num = 0
        print json_dict
        logging.info("没有评论"+json_text)
    if(comments_num % 20 == 0):
        page = comments_num / 20
    else:
        page = int(comments_num / 20) + 1
    print("共有%d页评论!" % page)
    if(comments_num == 0):
        print json_dict
        logging.info("没有评论"+json_text)

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


def get_comments_from_id(songId, userId):
    all_comments_list = get_all_comments(songId)
    comments = []
    for comment in all_comments_list:
        if (userId == comment['userID']):
            comments.append(comment)
    return comments


def get_all_playlist(userId):
    url = 'http://music.163.com/weapi/user/playlist?csrf_token='
    params = get_params_playlist(userId)
    json_text = get_json(url, params)
    json_dict = json.loads(json_text)
    playlist = []
    pl_dict = json_dict['playlist']
    for i in range(0, len(pl_dict)):
        listname = {'id': pl_dict[i]['id'], 'name': pl_dict[i]['name']}
        playlist.append(listname)
    return playlist


def get_all_songs(playlistId):
    url = "http://music.163.com/weapi/playlist/detail"
    params = get_params_songs(playlistId)
    json_dict = get_json(url, params)
    tracks = json_dict['result']['tracks']
    songlist = []
    for track in tracks:
        song = {'id': track['id'], 'name': track['name']}
        songlist.append(song)
    return songlist


# 将评论写入文本文件
def save_to_file(comment_list, filename):
        with codecs.open(filename, 'a', encoding='utf-8') as f:
            f.writelines(comment_list)
        print("写入文件成功!")


if __name__ == "__main__":
    start_time = time.time()  # 开始时间
    filename = u"list2.txt"
    userId = '98830806'
    playlist = get_all_playlist(userId)
    all_songs = []
    for li in playlist:
        songs_list = get_all_songs(li['id'])
        all_songs.extend(songs_list)
    with open('songs.json', 'w') as f:
        json.dump(all_songs, f)

    comments = get_comments_from_id('448184048', 46834350)
    with open('comments.json', 'w') as f:
        json.dump(comments, f)
    end_time = time.time()  # 结束时间
    print("程序耗时%f秒." % (end_time - start_time))
