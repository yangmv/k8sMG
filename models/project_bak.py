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

project_m2m_env = Table('project_m2m_env',Base.metadata,
    Column('project_id',Integer,ForeignKey('project.id')),
    Column('env_id',Integer,ForeignKey('env.id'))
)

project_m2m_owner = Table('project_m2m_owner',Base.metadata,
    Column('project_id',Integer,ForeignKey('project.id')),
    Column('user_id',Integer,ForeignKey('user.id'))
)


class Publish(Base):
    '''发布表'''
    __tablename__ = 'publish'
    id = Column(Integer, primary_key=True, autoincrement=True)
    desc = Column(Text(),nullable=True)
    status = Column(String(8),default='0')
    ctime = Column(DateTime(), default=datetime.now)
    name = Column(String(32))  #任务名,如 flask-demo #52
    job_id = Column(Integer)
    logs = Column(Text(),nullable=True)  #执行的日志
    start_exe_time = Column(DateTime())
    end_exe_time = Column(DateTime())
    ## step_current = Column(Integer,default=0)  #任务流

    env_id = Column(Integer,ForeignKey('env.id'))
    env = relationship("Env",foreign_keys=[env_id])

    project_id = Column(Integer,ForeignKey('project.id'))
    project = relationship("Project",foreign_keys=[project_id])

    review_user_id = Column(Integer,ForeignKey('user.id'))
    review_user = relationship("User",foreign_keys=[review_user_id])
    review_time = Column(DateTime())    #审核时间

    submit_user_id = Column(Integer,ForeignKey('user.id'))
    submit_user = relationship("User",foreign_keys=[submit_user_id])
    def __repr__(self):
        return '%s:%s'%(self.project.name,self.id)

class Project(Base):
    '''项目表'''
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)
    domain = Column(String(32))
    port = Column(String(32))
    replicas = Column(Integer,default=2)
    desc = Column(Text(),nullable=True)
    git_url = Column(String(64))
    git_user = Column(String(16))
    git_pwd = Column(String(32))
    env = relationship("Env",secondary=project_m2m_env,backref="project")
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


#ORM创建表结构
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:chaBUljXrcyn74F@172.16.0.121:3306/k8s_ops?charset=utf8', encoding='utf-8',echo=True)

def create():
    Base.metadata.create_all(engine)
def drop():
    Base.metadata.drop_all(engine)

if __name__ == '__main__':
    #drop()
    create()
