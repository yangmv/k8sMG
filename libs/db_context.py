#!/usr/bin/env python
# -*-coding:utf-8-*-
import sys
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append("..")
from settings import app_settings

def get_db_engine(dbkey):
    db_conf = app_settings['databases'][dbkey]
    dbuser = db_conf['user']
    dbpwd = db_conf['pwd']
    dbhost = db_conf['host']
    dbport = db_conf.get('port', 3306)
    dbname = db_conf['name']
    return create_engine('mysql+pymysql://{user}:{pwd}@{host}:{port}/{dbname}?charset=utf8'
                         .format(user=dbuser, pwd=quote_plus(dbpwd), host=dbhost, port=dbport, dbname=dbname),
                         logging_name=dbkey)

class DBContext(object):
    def __init__(self, dbkey):
        self.__engine = get_db_engine(dbkey)

    def __enter__(self):
        self.__session = sessionmaker(bind=self.__engine)()
        return self.__session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.close()

    def get_session(self):
        return self.__session