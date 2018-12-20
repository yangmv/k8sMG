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
from tornado import gen
import time

class WebSocketHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")
        # #交给LISTENES进行监听,监听增量内容
        # LISTENERS.append(self)
        pass

    def tail_file(self):
        while True:
            where = self.stdout_file.tell()
            line = self.stdout_file.readline()
            #监听是否有新内容进来
            if not line:
                self.stdout_file.seek(where)
                #print('no data')
                time.sleep(5)
            else:
                print('new --->',line)
                #print('LISTENERS--->',LISTENERS)
                self.write_message(line)

    def on_message(self, message):
        task_id = message
        print('task_id---->',task_id)
        #第一次进来先读取所有
        STDOUT_FILENAME = os.path.abspath('logs/tail.log')
        out_file = STDOUT_FILENAME
        self.stdout_file = open(STDOUT_FILENAME)
        self.stdout_file.seek(os.path.getsize(STDOUT_FILENAME))

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
        print('firt ok...')
        self.tail_file()

    def on_close(self):
        print("WebSocket closed")
        # try:
        #     LISTENERS.remove(self)
        # except:
        #     pass
        pass

class WsTestHandler(BaseHandler):
    def get(self):
        self.render('index.html')




index_urls = [
    (r'/ws/', WebSocketHandler),
    (r'/ws_test/', WsTestHandler)
]


