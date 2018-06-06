#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: pr.py
# Time: Mon May 21 18:20:00 2018
# Author: Rengui Wang <futurewrg@gmail.com>
import json
import io

file = io.open('comments.json', 'r', encoding='utf-8')
info = json.load(file)
with io.open("c.json", 'w', encoding="utf-8") as outfile:
    outfile.write(unicode(json.dumps(info, ensure_ascii=False)))
for i in info:
    print i['comment']
