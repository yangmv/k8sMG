#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: index_hanler.py
@time: 18/11/2下午4:54
'''
from libs.base_handler import BaseHandler
from libs.db_context import DBContext
from models.project import Project,Env,User,model_to_dict
import json

class UserHandler(BaseHandler):
    '''获取ENV信息'''
    def get(self):
        ret = dict(status=True,msg=None,data=None)
        try:
            with DBContext('readonly') as session:
                res = session.query(User).all()
                ret['data'] = [model_to_dict(item) for item in res]
                ret['msg'] = '获取资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

class EnvHandler(BaseHandler):
    '''获取ENV信息'''
    def get(self):
        ret = dict(status=True,msg=None,data=None)
        try:
            with DBContext('readonly') as session:
                res = session.query(Env).all()
                ret['data'] = [model_to_dict(item) for item in res]
                ret['msg'] = '获取资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

class ListHandler(BaseHandler):
    def get(self, args=None):
        '''获取project信息'''
        ret = dict(status=True,msg=None,data=None)
        try:
            with DBContext('readonly') as session:
                if args:
                    project_info = session.query(Project).filter(Project.id == args).first()
                    if not project_info:
                        ret['msg'] = '资源不存在'
                        raise Exception
                    project_list = model_to_dict(project_info)
                    project_list['cuser'] = project_info.cuser.name
                    project_list['env'] = [item.id for item in project_info.env]
                    project_list['owner'] = [item.id for item in project_info.owner]
                else:
                    project_all = session.query(Project).all()
                    project_list = []
                    for line in project_all:
                        new_line = model_to_dict(line)
                        new_line['cuser'] =  line.cuser.name
                        new_line['env'] = [item.id for item in line.env]
                        new_line['env_list'] = [model_to_dict(item) for item in line.env]
                        new_line['owner'] = [item.id for item in line.owner]
                        new_line['owner_list'] = [model_to_dict(item) for item in line.owner]
                        project_list.append(new_line)
                ret['data'] = project_list
                ret['msg'] = '获取资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)


    def post(self, *args, **kwargs):
        '''新增project'''
        ret = dict(status=True,msg=None,data=None)
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            name = data.get("name", None)
            domain = data.get("domain", None)
            port = data.get("port", None)
            replicas = data.get("replicas", None)
            desc = data.get("desc", None)
            git_url = data.get("git_url", None)
            git_user = data.get("git_user", None)
            git_pwd = data.get("git_pwd", None)
            env_list = data.get("env", None)
            owner_list = data.get("owner", None)
            cuser_id = data.get("cuser_id", None)

            check = [name,domain,port,replicas,git_url,git_user,git_pwd,env_list,owner_list,cuser_id]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                raise Exception

            with DBContext('default') as session:
                project = Project(
                    name=name,
                    domain=domain,
                    port=port,
                    replicas=replicas,
                    desc=desc,
                    git_url=git_url,
                    git_user=git_user,
                    git_pwd=git_pwd,
                    cuser_id=cuser_id
                )
                project.env = session.query(Env).filter(Env.id.in_(env_list)).all()
                project.owner = session.query(User).filter(User.id.in_(owner_list)).all()
                session.add(project)
                session.commit()
                ret['data'] = model_to_dict(project)
                ret['msg'] = '新增资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

    def put(self,args=None):
        '''更新project'''
        ret = dict(status=True,msg=None,data=None)
        try:
            if not args:
                ret['msg'] = 'arg缺少必要参数'
                raise Exception
            data = json.loads(self.request.body.decode("utf-8"))
            name = data.get("name", None)
            domain = data.get("domain", None)
            port = data.get("port", None)
            replicas = data.get("replicas", None)
            desc = data.get("desc", None)
            git_url = data.get("git_url", None)
            git_user = data.get("git_user", None)
            git_pwd = data.get("git_pwd", None)
            env_list = data.get("env", None)
            owner_list = data.get("owner", None)

            check = [name,domain,port,replicas,git_url,git_user,git_pwd,env_list,owner_list]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                raise Exception

            with DBContext('default') as session:
                project = session.query(Project).filter(Project.id == args).first()
                if not project:
                    ret['msg'] = '资源不存在'
                    raise Exception
                project.name = name
                project.domain = domain
                project.port = port
                project.replicas = replicas
                project.desc = desc
                project.git_url = git_url
                project.git_user = git_user
                project.git_pwd = git_pwd
                project.env = session.query(Env).filter(Env.id.in_(env_list)).all()
                project.owner = session.query(User).filter(User.id.in_(owner_list)).all()

                session.commit()
                ret['data'] = model_to_dict(project)
                ret['msg'] = '更新资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

    def patch(self, *args, **kwargs):
        print('更新局部')
        self.write(dict(status=0, msg='patch'))

    def delete(self, args=None):
        ret = dict(status=True,msg=None,data=None)
        try:
            if not args:
                ret['msg'] = 'arg缺少必要参数'
                raise Exception
            with DBContext('default') as session:
                project = session.query(Project).filter(Project.id == args).first()
                if not project:
                    ret['msg'] = '资源不存在'
                    raise
                session.delete(project)
                session.commit()
                ret['data'] = model_to_dict(project)
                ret['msg'] = '删除资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)


index_urls = [
    (r"/api/project/?(\w+)?/", ListHandler),
    (r"/api/env/", EnvHandler),
    (r"/api/user/", UserHandler),
]
