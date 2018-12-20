#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: index_hanler.py
@time: 18/11/2下午4:54
'''
from libs.base_handler import BaseHandler
import os
from tornado.websocket import WebSocketHandler

class WebSocketHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")
        #交给LISTENES进行监听,监听增量内容
        LISTENERS.append(self)

    def on_message(self, message):
        print('get_msg--->',message)
        #第一次进来先读取所有
        out_file = STDOUT_FILENAME
        print(out_file)
        if os.path.getsize(out_file) > 10240000:
            self.write_message('file is too large!')
        else:
            with open(out_file,'r') as f:
                f.seek(0,os.SEEK_END)
                fsize = f.tell()
                f.seek(max(fsize - 1024, 0), 0)
                for line in f.readlines()[-800:]:
                    self.write_message(line)

    def on_close(self):
        print("WebSocket closed")
        try:
            LISTENERS.remove(self)
        except:
            pass

class WsTestHandler(BaseHandler):
    def get(self):
        self.render('index.html')


def tail_file():
    where = stdout_file.tell()
    line = stdout_file.readline()
    #监听是否有新内容进来
    if not line:
        stdout_file.seek(where)
    else:
        #print('LISTENERS--->',LISTENERS)
        for element in LISTENERS:
            element.write_message(line)


LISTENERS = []
STDOUT_FILENAME = os.path.abspath('logs/tail.log')
stdout_file = open(STDOUT_FILENAME)
stdout_file.seek(os.path.getsize(STDOUT_FILENAME))


index_urls = [
    (r'/ws/', WebSocketHandler),
    (r'/ws_test/', WsTestHandler)
]


