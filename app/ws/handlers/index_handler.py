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
from settings import BASE_DIR

class WebSocketHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print('get_msg--->',message)
        #第一次进来先读取所有
        task_id = message
        try:
            out_file = '%s/logs/%s.log'%(BASE_DIR,task_id)
            check_exit = os.path.exists(out_file)
            if not check_exit:
                open(out_file,'a').close()
            stdout_file = open(out_file)
            stdout_file.seek(os.path.getsize(out_file))
            if os.path.getsize(out_file) > 10240000:
                self.write_message('file is too large!')
            else:
                with open(out_file,'r') as f:
                    for line in f.readlines():
                        self.write_message(line)
            if task_id in LISTENERS:
                LISTENERS[task_id]['ele'].append(self)
            else:
                LISTENERS[task_id] = {
                    'ele':[self],
                    'stdout_file': stdout_file
                }
            self.task_id = task_id
        except Exception as e:
            self.write_message(str(e))

    def on_close(self):
        print("WebSocket closed")
        try:
            LISTENERS[self.task_id]['ele'].remove(self)
            if not LISTENERS[self.task_id]['ele']:
                LISTENERS[self.task_id]['stdout_file'].close()
                LISTENERS.pop(self.task_id)
        except:
            pass

class WsTestHandler(BaseHandler):
    def get(self):
        self.render('index.html')


def tail_file():
    for line in LISTENERS:
        stdout_file = LISTENERS[line]['stdout_file']
        ele_list = LISTENERS[line]['ele']
        if ele_list:
            where = stdout_file.tell()
            line = stdout_file.readline()
            #监听是否有新内容进来
            if not line:
                stdout_file.seek(where)
            else:
                #print('new-->',line)
                for element in ele_list:
                    element.write_message(line)
        else:
            LISTENERS.pop(line)

LISTENERS = {}


index_urls = [
    (r'/v1/k8s/ws/', WebSocketHandler),
    (r'/ws_test/', WsTestHandler)
]


