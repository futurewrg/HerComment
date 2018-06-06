#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: proxy.py
# Time: Mon May 21 19:51:49 2018
# Author: Rengui Wang <futurewrg@gmail.com>

import random

import requests
import urllib2
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding("utf8")

user_agent_list = []
with open('Chrome.txt', 'r') as f:
    user_agent_list.append(f.readline()[0:-1])
print user_agent_list

http_proxies = []
test_url = "http://www.baidu.com/js/bdsug.js?v=1.0.3.0"


def get_ua():
    ua = random.choice(user_agent_list)
    return ua


def test_proxy(proxy):
    try:
        response = requests.get(test_url, timeout=1,
                                allow_redirects=False, proxies={"http": proxy})
        if response.status_code == 200 and\
           response.content.index("function") > -1:
            http_proxies.append(proxy)
    except Exception, e:
        print "验证代理IP异常：" + str(e)


def get_new_proxies():
    xici_urls = [
        "http://www.xicidaili.com/nn/1",
        "http://www.xicidaili.com/nn/2",
        "http://www.xicidaili.com/nn/3",
        "http://www.xicidaili.com/nn/4",
    ]

    for url in xici_urls:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        referer = 'http://www.zhihu.com/articles'
        headers = {"User-Agent": user_agent, 'Referer': referer}
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        soup = BeautifulSoup(response.read(), "lxml")
        table = soup.find("table", attrs={"id": "ip_list"})
        trs = table.find_all("tr")
        proxys = []
        for i in range(1, len(trs)):
            tr = trs[i]
            tds = tr.find_all("td")
            ip = tds[1].text
            port = tds[2].text
            desc = tds[4].text
            if desc.encode('utf-8') == "高匿":
                proxy = "http://" + ip + ":" + port
                proxys.append(proxy)
                # noinspection PyBroadException
        with ThreadPoolExecutor(40) as executor:
            executor.map(test_proxy, proxys)


def change_proxy(invalid_proxy):
    # 删除无用代理
    if invalid_proxy in http_proxies:
        http_proxies.remove(invalid_proxy)

    # 没有可用代理，需要重新从西刺代理获取
    while len(http_proxies) == 0:
        print "没有可用代理，开始重新获取..."
        get_new_proxies()
        print "本次获取到有效代理IP：" + str(http_proxies)

    proxy = random.choice(http_proxies)
    return proxy


def get_proxy():
    # 没有可用代理，需要重新从西刺代理获取
    while len(http_proxies) == 0:
        print "没有可用代理，开始重新获取..."
        get_new_proxies()
        print "本次获取到有效代理IP：" + str(http_proxies)
    proxy = random.choice(http_proxies)
    return proxy


if __name__ == "__main__":
    proxy = get_proxy()
    print proxy
    proxy = change_proxy(proxy)
    print proxy
