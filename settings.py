#!/usr/bin/env python
#encoding:utf-8
import os

BASE_DIR = os.path.dirname(__file__)


app_settings = {
    "template_path": ".",
    'debug' : True,
    'xsrf_cookies' : False,
    'databases' : {
        'default': {
            'host' : '172.16.0.121',
            'port' : 3306,
            'user' : 'root',
            'pwd' : 'xxx',
            'name' : 'k8s_ops',
        },
        'readonly': {
            'host' : '172.16.0.121',
            'port' : 3306,
            'user' : 'root',
            'pwd' : 'xxx',
            'name' : 'k8s_ops',
        }
    },
    'redises' : {
        'default': {
            'host': '172.16.0.121',
            'port': '6379',
            'db': 6,
            'auth': True,
            'charset': 'utf-8',
            'password': ''
        }
    },
    'mqs' : {
        'default': {
            'MQ_ADDR': '172.16.0.121',
            'MQ_PORT': 5672,
            'MQ_VHOST': '/',
            'MQ_USER': 'sz',
            'MQ_PWD': '123456',
        }
    },
}


jenkins_conf = {
    'url' : 'http://xxx.com',
    'user' : 'admin',
    'pwd' : 'xxx'
}