#!/usr/bin/env python
# -*-coding:utf-8-*-
import shortuuid
from libs.cache import get_cache
from tornado.web import RequestHandler, HTTPError

class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        self.new_csrf_key = str(shortuuid.uuid())
        super(BaseHandler, self).__init__(*args, **kwargs)

    def prepare(self):
        '''
            这里重写了RequestHandler的prepare方法
            prepare方法是在get/post请求前执行
        '''
        # 验证客户端CSRF，如请求为GET，则不验证，否则验证。最后将写入新的key
        cache = get_cache()
        if self.request.method != 'GET':
            csrf_key = self.get_cookie('csrf_key')
            pipeline = cache.get_pipeline()
            result = cache.get(csrf_key, private=False, pipeline=pipeline)
            cache.delete(csrf_key, private=False, pipeline=pipeline)
            if result != '1':
                raise HTTPError(400, 'csrf error')

        cache.set(self.new_csrf_key, 1, expire=1800, private=False)
        self.set_cookie('csrf_key', self.new_csrf_key)

