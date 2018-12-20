#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
Author : ss
date   : 2018年4月11日
role   : 缓存
"""

import base64
import json
import redis
from shortuuid import uuid
from settings import app_settings as my_settings
from libs.tools import singleton, bytes_to_unicode, convert


@singleton
class Cache(object):
    def __init__(self):
        self.__redis_connections = {}
        redis_configs = my_settings['redises']
        for config_key, redis_config in redis_configs.items():
            auth = redis_config['auth']
            host = redis_config['host']
            port = redis_config['port']
            db = redis_config['db']
            return_utf8 = False
            if 'decode_responses' in redis_config:
                return_utf8 = redis_config['decode_responses']
            password = redis_config['password']

            if auth:
                redis_conn = redis.Redis(host=host,
                                         port=port, db=db,
                                         password=password,
                                         decode_responses=return_utf8)
            else:
                redis_conn = redis.Redis(host=host, port=port, db=db, decode_responses=return_utf8)
            self.__redis_connections[config_key] = redis_conn

        self.__salt = str(uuid())

    def set(self, key, value, expire=-1, conn_key='default', private=True, pipeline=None):
        real_key = self.__get_key(key, private)
        execute_main = self.__get_execute_main(conn_key, pipeline)
        if expire > 0:
            execute_main.set(real_key, value, ex=expire)
        else:
            execute_main.set(real_key, value)

    def set_json(self, key, value, expire=-1, conn_key='default', private=True, pipeline=None):
        value = json.dumps(value)
        value = base64.b64encode(value.encode('utf-8'))
        self.set(key, value, expire, conn_key, private, pipeline)

    def get(self, key, default='', conn_key='default', private=True, pipeline=None):
        real_key = self.__get_key(key, private)
        execute_main = self.__get_execute_main(conn_key, pipeline)
        if execute_main.exists(real_key):
            result = execute_main.get(real_key)
            return bytes_to_unicode(result)
        return default

    def incr(self, key, private=True,
             conn_key='default', amount=1):
        real_key = self.__get_key(key, private)
        execute_main = self.__get_execute_main(conn_key, None)
        if execute_main.exists(real_key):
            execute_main.incr(real_key, amount=amount)
            return self.get(key, default='0',
                            private=private, conn_key=conn_key)
        return None

    def get_json(self, key, default='',
                 conn_key='default', private=True):
        result = self.get(key, default, conn_key, private)
        result = base64.b64decode(result)
        result = bytes_to_unicode(result)
        if result:
            result = json.loads(result)
        return result

    def delete(self, *keys, conn_key='default', private=True, pipeline=None):
        execute_main = self.__get_execute_main(conn_key, pipeline)
        _keys = [self.__get_key(key, private) for key in keys]
        return execute_main.delete(*_keys)

    def clear(self, conn_key='default'):
        execute_main = self.__get_execute_main(conn_key, None)
        execute_main.flushdb()

    def get_pipeline(self, conn_key='default'):
        return self.__redis_connections[conn_key].pipeline()

    def execute_pipeline(self, pipeline):
        if pipeline:
            return pipeline.execute()

    def get_conn(self, conn_key='default'):
        return self.__get_execute_main(conn_key)

    def hgetall(self, key, default='', conn_key='default', private=True):
        real_key = self.__get_key(key, private)
        execute_main = self.__get_execute_main(conn_key, None)
        if execute_main.exists(real_key):
            result = execute_main.hgetall(real_key)
            result = convert(result)
        else:
            return default
        return result

    @property
    def redis(self):
        return self.__get_execute_main()

    def __get_key(self, key, private=True):
        if private:
            return '%s%s' % (self.__salt, key)
        else:
            return key

    def __get_execute_main(self, conn_key='default', pipeline=None):
        if pipeline:
            return pipeline
        return self.__redis_connections[conn_key]


def get_cache():
    return Cache()





