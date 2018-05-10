#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: user.py
# Time: Tue May  8 22:03:22 2018
# Author: Rengui Wang <futurewrg@gmail.com>

import json
import codecs
import time
import comment

userId = '46834350'


def readList(filename):
    playlist = []
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        text = f.readlines()
        for l in text:
            line = l.split()
            playlist.append(line[1])
    return playlist


if __name__ == "__main__":
    start_time = time.time()  # 开始时间
    userId = 98830806
    playlist = readList('list.txt')
    print playlist
    all_songs = []
    for li in playlist:
        songs_list = comment.get_all_songs(li)
        all_songs.extend(songs_list)
    print "所有列表共包含 %d 首歌." % len(all_songs)
    with open('songs.json', 'w') as f:
        json.dump(all_songs, f)
    comments = []
    i = 1
    for song in all_songs:
        print '搜索第 %d 首...' % i
        i = i+1
        com = comment.get_comments_from_id(song['id'], userId)
        comments.extend(com)
    with open('comments.json', 'w') as f:
        json.dump(comments, f)
    end_time = time.time()  # 结束时间
    print("程序耗时%f秒." % (end_time - start_time))
