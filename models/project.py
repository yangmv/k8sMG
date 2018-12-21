#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: project.py
@time: 18/11/3下午12:14
'''
from sqlalchemy import Column,String,Integer,Boolean,DateTime,Text,ForeignKey,Table
from sqlalchemy.orm import relationship,class_mapper
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from datetime import date

def model_to_dict(model):
    model_dict = {}
    for key, column in class_mapper(model.__class__).c.items():
        val = getattr(model, key, None)
        if isinstance(val,datetime):
            val = val.strftime('%Y-%m-%d %H:%M:%S')
            #val = val.strftime('%Y-%m-%d')
        elif isinstance(val, date):
            val = val.strftime("%Y-%m-%d")
        model_dict[column.name] = val
    return model_dict


Base = declarative_base()

publish_m2m_app = Table('publish_m2m_app',Base.metadata,
    Column('publish_id',Integer,ForeignKey('publish.id')),
    Column('app_id',Integer,ForeignKey('app.id'))
)

project_m2m_app = Table('project_m2m_app',Base.metadata,
    Column('project_id',Integer,ForeignKey('project.id')),
    Column('app_id',Integer,ForeignKey('app.id'))
)

project_m2m_env = Table('project_m2m_env',Base.metadata,
    Column('project_id',Integer,ForeignKey('project.id')),
    Column('env_id',Integer,ForeignKey('env.id'))
)

project_m2m_owner = Table('project_m2m_owner',Base.metadata,
    Column('project_id',Integer,ForeignKey('project.id')),
    Column('user_id',Integer,ForeignKey('user.id'))
)


class Task(Base):
    '''任务表'''
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True)

    publish_id = Column(Integer,ForeignKey('publish.id'))
    publish = relationship("Publish",foreign_keys=[publish_id])
    env_id = Column(Integer,ForeignKey('env.id'))
    env = relationship("Env",foreign_keys=[env_id])
    app_id = Column(Integer,ForeignKey('app.id'))
    app = relationship("App",foreign_keys=[app_id])

    name = Column(String(32))  #任务名,如 flask-demo #52
    job_id = Column(Integer)
    logs = Column(Text(),nullable=True)  #执行的日志
    start_exe_time = Column(DateTime())
    end_exe_time = Column(DateTime())
    status = Column(String(8),default='0')



class Publish(Base):
    '''发布表'''
    __tablename__ = 'publish'
    id = Column(Integer, primary_key=True, autoincrement=True)
    desc = Column(Text(),nullable=True)
    status = Column(String(8),default='0')      #0未执行,11测试执行中,12测试执行完毕,13测试执行失败,2审核通过,31正式执行中,32正式执行完毕,33正式执行失败,4所有完毕
    ctime = Column(DateTime(), default=datetime.now)

    app = relationship("App",secondary=publish_m2m_app,backref="publish")

    project_id = Column(Integer,ForeignKey('project.id'))
    project = relationship("Project",foreign_keys=[project_id])

    review_user_id = Column(Integer,ForeignKey('user.id'))
    review_user = relationship("User",foreign_keys=[review_user_id])
    review_time = Column(DateTime())    #审核时间

    submit_user_id = Column(Integer,ForeignKey('user.id'))
    submit_user = relationship("User",foreign_keys=[submit_user_id])
    def __repr__(self):
        return '%s:%s'%(self.project.name,self.id)

class App(Base):
    '''应用表'''
    __tablename__ = 'app'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)
    port = Column(String(32))
    desc = Column(Text(),nullable=True)
    git_url = Column(String(64))
    ctime = Column(DateTime(), default=datetime.now)
    status = Column(String(8),default='0')
    cuser_id = Column(Integer,ForeignKey('user.id'))
    cuser = relationship("User",foreign_keys=[cuser_id])
    def __repr__(self):
        return '%s:%s'%(self.id,self.name)

class Project(Base):
    '''项目表'''
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)
    desc = Column(Text(),nullable=True)
    app = relationship("App",secondary=project_m2m_app,backref="project")
    env = relationship("Env",secondary=project_m2m_env,backref="project")   #准备去掉
    owner = relationship("User",secondary=project_m2m_owner,backref="project")
    ctime = Column(DateTime(), default=datetime.now)
    status = Column(String(8),default='0')
    cuser_id = Column(Integer,ForeignKey('user.id'))
    cuser = relationship("User",foreign_keys=[cuser_id])
    def __repr__(self):
        return '%s:%s'%(self.id,self.name)

class Env(Base):
    '''环境表'''
    __tablename__ = 'env'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    label = Column(String(32), unique=True)
    name = Column(String(32), unique=True)

class User(Base):
    '''人员表'''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)
    # 返回一个可以用来表示对象的可打印字符串
    def __repr__(self):
        return '%s:%s'%(self.id,self.name)
