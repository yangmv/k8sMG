#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: publish_jenkins.py
@time: 18/11/9下午2:17
'''
from libs.db_context import DBContext
from libs.jenkins_tools import JenkinsAPI
from models.project import Publish
import time
from settings import jenkins_conf,BASE_DIR
from datetime import datetime
from libs.tools import exec_shell

class TaskPublish():
    def __init__(self,task_obj):
        self.flag = True
        self.task_id = task_id

    def task_exec(self):
        '''发布任务'''
        try:
            with DBContext('default') as session:
                publish = session.query(Publish).filter(Publish.id == self.task_id).first()
                project_name = publish.project.name
                self.project_name = project_name
                # jenkins开始调度发布
                obj = JenkinsAPI()
                is_bulid = obj.check_is_build(project_name)
                if is_bulid:
                    publish.logs = '[%s]正在bulid中'%project_name
                    raise Exception

                else:
                    param_dict= {
                        'replicas': publish.project.replicas,
                        'domain': publish.project.domain,
                        'port': publish.project.port
                    }
                    print('param_dict->>>>>>>',param_dict)
                    #job_id = obj.build_job(project_name)
                    job_id = obj.build_job_param(project_name,param_dict)
                    time.sleep(10)  #给jenkins10秒缓冲时间
                    if job_id:
                        job_name = '%s #%s'%(project_name,job_id)
                        publish.name = job_name
                        publish.job_id = job_id
                        session.commit()
                        #print('发布任务提交成功')
                        while True:
                            time.sleep(0.5)
                            check_status = obj.check_is_build(project_name)
                            self.task_log(job_id)
                            if not check_status:
                                self.flag = False
                                break
                        publish.status = '3'    #完成
                        publish.logs = '发布完成'
                        publish.end_exe_time = datetime.now()
                    else:
                        #任务提交失败
                        publish.status = '-2'   #失败
                        publish.logs = '发布失败'
                    session.commit()
        except Exception as e:
            print('error-->>>')
            print(e)
            with DBContext('default') as session:
                publish = session.query(Publish).filter(Publish.id == self.task_id).first()
                publish.status = '-2'
                publish.logs = 'bulid异常终止'
                session.commit()


    def task_log(self,job_id):
        log_dir = '%s/logs'%BASE_DIR
        cmd = 'wget -c -t 10 %s/job/%s/%s/consoleText  --user=%s --password=%s --auth-no-challenge -O ' \
              '%s/%s.log'%(jenkins_conf['url'],self.project_name,job_id,jenkins_conf['user'],
                           jenkins_conf['pwd'],log_dir,self.task_id)
        #print(cmd)
        exec_shell(cmd)