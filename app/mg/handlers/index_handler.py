#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: index_hanler.py
@time: 18/11/2下午4:54
'''
from libs.base_handler import BaseHandler
from libs.db_context import DBContext
from models.project import Project,App,Env,User,model_to_dict
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

class indexListHandler(BaseHandler):
    def get(self, args=None):
        '''获取project信息'''
        ret = dict(status=True,msg=None,data=None)
        try:
            with DBContext('readonly') as session:
                if args:
                    obj = session.query(Project).filter(Project.id == args).first()
                    if not obj:
                        ret['msg'] = '资源不存在'
                        raise Exception
                    data = model_to_dict(obj)
                    data['cuser'] = obj.cuser.name
                    data['app'] = [item.id for item in obj.app]
                    #data['env'] = [item.id for item in obj.env]
                    data['owner'] = [item.id for item in obj.owner]
                else:
                    obj = session.query(Project).all()
                    data = []
                    for line in obj:
                        new_line = model_to_dict(line)
                        new_line['cuser'] =  line.cuser.name
                        new_line['app'] = [item.id for item in line.app]
                        new_line['app_list'] = [model_to_dict(item) for item in line.app]
                        #new_line['env'] = [item.id for item in line.env]
                        #new_line['env_list'] = [model_to_dict(item) for item in line.env]
                        new_line['owner'] = [item.id for item in line.owner]
                        new_line['owner_list'] = [model_to_dict(item) for item in line.owner]
                        data.append(new_line)
                ret['data'] = data
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
            name = data.get("name")
            desc = data.get("desc")
            app_list = data.get("app")
            #env_list = data.get("env")
            owner_list = data.get("owner")
            cuser_id = data.get("cuser_id")

            print(app_list)
            check = [name,app_list,owner_list,cuser_id]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                return self.write(ret)
                #raise Exception

            with DBContext('default') as session:
                obj = Project(
                    name=name,
                    desc=desc,
                    cuser_id=cuser_id
                )
                obj.app = session.query(App).filter(App.id.in_(app_list)).all()
                #obj.env = session.query(Env).filter(Env.id.in_(env_list)).all()
                obj.owner = session.query(User).filter(User.id.in_(owner_list)).all()
                session.add(obj)
                session.commit()
                ret['data'] = model_to_dict(obj)
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

            name = data.get("name")
            desc = data.get("desc")
            app_list = data.get("app")
            #env_list = data.get("env")
            owner_list = data.get("owner")


            check = [name,app_list,owner_list]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                raise Exception

            with DBContext('default') as session:
                obj = session.query(Project).filter(Project.id == args).first()
                if not obj:
                    ret['msg'] = '资源不存在'
                    raise Exception
                obj.name = name
                obj.desc = desc
                obj.app = session.query(App).filter(App.id.in_(app_list)).all()
                #obj.env = session.query(Env).filter(Env.id.in_(env_list)).all()
                obj.owner = session.query(User).filter(User.id.in_(owner_list)).all()

                session.commit()
                ret['data'] = model_to_dict(obj)
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
                    raise Exception
                session.delete(project)
                session.commit()
                ret['data'] = model_to_dict(project)
                ret['msg'] = '删除资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

# index_urls = [
#     (r"/v1/k8s/project/?(\w+)?/", ListHandler),
#     (r"/v1/k8s/env/", EnvHandler),
#     (r"/v1/k8s/user/", UserHandler)
# ]
