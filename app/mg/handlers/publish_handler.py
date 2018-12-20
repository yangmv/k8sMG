#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: index_hanler.py
@time: 18/11/2下午4:54
'''
from libs.base_handler import BaseHandler
from libs.db_context import DBContext
from models.project import App,Project,Env,User,model_to_dict,Publish,Task
import json
from datetime import datetime
from libs.jenkins_tools import JenkinsAPI
from libs.mqhelper import MessageQueueBase

class TaskHandler(BaseHandler):
    def get(self,*args,**kwargs):
        '''获取task信息'''
        ret = dict(status=True,msg=None,data=None)
        try:
            publish_id = self.get_argument('publish_id',None)
            app_id = self.get_argument('app_id',None)
            env_id = self.get_argument('env_id',None)
            if not publish_id or not app_id or not env_id:
                ret['msg'] = '缺少参数'
                raise Exception
            with DBContext('readonly') as session:
                res = session.query(Task).filter(Task.publish_id == publish_id,
                                                 Task.app_id == app_id,Task.env_id == env_id).first()
                if not res:
                    ret['msg'] = '资源不存在'
                    raise Exception
                print(res.name)
                print(res.status)
                ret['data'] = model_to_dict(res)
                ret['msg'] = '获取资源成功'

        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)


class JobLogHandler(BaseHandler):
    def get(self,*args,**kwargs):
        '''获取job信息'''
        ret = dict(status=True,msg=None,data=None)
        try:
            project_name = self.get_argument('project_name',None)
            job_id = self.get_argument('job_id',None)
            if not project_name or not job_id:
                ret['msg'] = '缺少参数'
                raise Exception
            obj = JenkinsAPI()
            data = obj.get_job_log(project_name,job_id)
            ret['data'] = json.dumps(data.split('\n'))
            ret['msg'] = '[project]%s [job_id]%s 日志获取成功!'%(project_name,job_id)

        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

class JobExecHandler(BaseHandler):
    def post(self,args=None):
        '''执行job任务'''
        ret = dict(status=True,msg=None,data=None)
        try:
            if not args:
                ret['msg'] = 'arg缺少必要参数'
                raise Exception

            ### 发送消息(生产者,生产了一条消息,消费者会去消费掉)
            ### 消息内容为[task ID]
            task_id = args
            with MessageQueueBase('task_sced', 'direct', 'the_task') as save_paper_channel:
                save_paper_channel.publish_message(task_id)   #告知MQ执行此TaskSched
            ret['msg'] = 'Task creation success, ID：%s'%task_id

        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

class PublishHandler(BaseHandler):
    def get(self, args=None):
        '''获取发布列表'''
        ret = dict(status=True,msg=None,data=None)
        try:
            with DBContext('readonly') as session:
                if args:
                    res = session.query(Publish).filter(Publish.id == args).first()
                    if not res:
                        ret['msg'] = '资源不存在'
                        raise Exception
                    res_list = model_to_dict(res)
                    res_list['project'] = res.project.name
                    res_list['review_user'] = res.review_user.name
                    res_list['submit_user'] = res.submit_user.name
                    res_list['app_list'] = [model_to_dict(item) for item in res.app]
                else:
                    res_list = []
                    res = session.query(Publish).all()
                    for line in res:
                        new_item = model_to_dict(line)
                        new_item['project'] = line.project.name
                        new_item['review_user'] = line.review_user.name
                        new_item['submit_user'] = line.submit_user.name
                        new_item['app_list'] = [model_to_dict(item) for item in line.app]
                        res_list.append(new_item)
            ret['data'] = res_list
            ret['msg'] = '获取资源成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

    def post(self, *args, **kwargs):
        '''提交publish任务'''
        ret = dict(status=True,msg=None,data=None)
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            project_id = data.get("project_id")
            #project_name = data.get("project_name", None)
            submit_user_id = data.get("submit_user_id")
            review_user_id = data.get("review_user_id")
            desc = data.get("desc")
            app_list = data.get("app")
            print(app_list)

            check = [project_id,submit_user_id,review_user_id,app_list]
            if not all(check):
                ret['msg'] = '必要字段不能为空'
                raise Exception
            with DBContext('default') as session:
                obj = Publish(
                    project_id = project_id,
                    submit_user_id = submit_user_id,
                    review_user_id = review_user_id,
                    desc = desc
                )
                obj.app = session.query(App).filter(App.id.in_(app_list)).all()
                session.add(obj)
                session.commit()
                ret['data'] = model_to_dict(obj)
                ret['msg'] = '发布任务提交成功'

        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)

    def patch(self,args=None):
        '''更新任务状态'''
        ret = dict(status=True,msg=None,data=None)
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            status = data.get('status')
            with DBContext('default') as session:
                res = session.query(Publish).filter(Publish.id == args).first()
                res.status = status
                res.review_time = datetime.now()
                session.commit()
                ret['data'] = model_to_dict(res)
                ret['msg'] = '任务状态更新成功'
        except Exception as e:
            print(e)
            ret['status'] = False
            if not ret['msg']:ret['msg'] = str(e)
        self.write(ret)


index_urls = [
    (r"/v1/k8s/publish/?(\w+)?/", PublishHandler),
    (r"/v1/k8s/job/log/", JobLogHandler),
    (r"/v1/k8s/job/exec/?(\w+)?/", JobExecHandler),
    (r"/v1/k8s/job/detail/", TaskHandler)
]
