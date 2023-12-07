#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: urls.py.py
@time: 2019-01-02 17:36
'''
from app.mg.handlers.index_handler import *
from app.mg.handlers.app_handle import *
from app.mg.handlers.publish_handler import *

mg_urls = [
    (r"/v1/k8s/project/?(\w+)?/", indexListHandler),
    (r"/v1/k8s/env/", EnvHandler),
    (r"/v1/k8s/user/", UserHandler),

    (r"/v1/k8s/app/?(\w+)?/", appListHandler),

    (r"/v1/k8s/publish/?(\w+)?/", PublishHandler),
    (r"/v1/k8s/job/log/", JobLogHandler),
    (r"/v1/k8s/job/exec/?(\w+)?/", JobExecHandler),
    (r"/v1/k8s/job/detail/", TaskHandler)
]