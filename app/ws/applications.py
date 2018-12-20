#!/usr/bin/env python
#encoding:utf-8
from libs.application import Application as myapplication
from app.ws.handlers.index_handler import index_urls

import tornado
from app.ws.handlers.index_handler import tail_file

class Application(myapplication):
    def __init__(self,**settings):
        urls = []
        urls.extend(index_urls)
        tailed_callback = tornado.ioloop.PeriodicCallback(tail_file, 500)
        tailed_callback.start()
        super(Application,self).__init__(urls,**settings)

if __name__ == '__main__':
    pass