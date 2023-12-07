#!/usr/bin/env python
#encoding:utf-8
from libs.application import Application as myapplication
from app.mg.urls import mg_urls
# from app.mg.handlers.index_handler import index_urls
# from app.mg.handlers.app_handle import index_urls as app_urls
# from app.mg.handlers.publish_handler import index_urls as publish_urls


class Application(myapplication):
    def __init__(self,**settings):
        urls = []
        urls.extend(mg_urls)
        # urls.extend(index_urls)
        # urls.extend(app_urls)
        # urls.extend(publish_urls)
        super(Application,self).__init__(urls,**settings)

if __name__ == '__main__':
    pass