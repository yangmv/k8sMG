#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: db_sync.py
@time: 18/12/21下午2:32
'''
from models.project import Base
from settings import app_settings

#ORM创建表结构
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8'%(
    app_settings['databases']['default'].get('user'),
    app_settings['databases']['default'].get('pwd'),
    app_settings['databases']['default'].get('host'),
    app_settings['databases']['default'].get('port'),
    app_settings['databases']['default'].get('name')
), encoding='utf-8',echo=True)

def create():
    Base.metadata.create_all(engine)
    print('[Success] 表结构创建成功!')
def drop():
    Base.metadata.drop_all(engine)

if __name__ == '__main__':
    create()