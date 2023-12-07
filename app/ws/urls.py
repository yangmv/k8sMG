#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: urls.py.py
@time: 2019-01-02 18:09
'''
from app.ws.handlers.index_handler import *

ws_urls = [
    (r'/v1/k8s/ws/', WebSocketHandler),
    (r'/ws_test/', WsTestHandler)
]