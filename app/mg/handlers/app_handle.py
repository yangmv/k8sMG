#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: index_hanler.py
@time: 18/11/2下午4:54
'''
from libs.base_handler import BaseHandler
from libs.db_context import DBContext
from models.project import App,Project,Env,User,model_to_dict
import json

class appListHandler(BaseHandler):
    def get(self, args=None):
        '''获取project信息'''
        ret = dict(status=True,msg=None,data=None)
        try:
            with DBContext('readonly') as session:
                if args:
                    obj = session.query(App).filter(Project.id == args).first()
                    if not obj:
                        ret['msg'] = '资源不存在'
                        raise Exception
                    data = model_to_dict(obj)
                    data['cuser'] = obj.cuser.name
                else:
                    obj = session.query(App).all()
                    data = []
                    for line in obj:
                        new_line = model_to_dict(line)
                        new_line['cuser'] =  line.cuser.name
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
            port = data.get("port")
            desc = data.get("desc")
            git_url = data.get("git_url")
            cuser_id = data.get("cuser_id")

            check = [name,port,git_url,cuser_id]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                raise Exception

            with DBContext('default') as session:
                obj = App(
                    name=name,
                    port=port,
                    desc=desc,
                    git_url=git_url,
                    cuser_id=cuser_id
                )
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
            port = data.get("port")
            desc = data.get("desc")
            git_url = data.get("git_url")

            check = [name,port,git_url]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                raise Exception

            with DBContext('default') as session:
                obj = session.query(App).filter(App.id == args).first()
                if not obj:
                    ret['msg'] = '资源不存在'
                    raise Exception
                obj.name = name
                obj.port = port
                obj.desc = desc
                obj.git_url = git_url
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
#     (r"/v1/k8s/app/?(\w+)?/", ListHandler)
# ]
