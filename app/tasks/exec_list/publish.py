#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: publish_jenkins.py
@time: 18/11/9下午2:17
'''
from libs.jenkins_tools import JenkinsAPI
import time
from settings import jenkins_conf,BASE_DIR
from libs.tools import exec_shell

class TaskPublish():
    def __init__(self,task_id,app_name,port,domain,env):
        self.flag = True
        self.task_id = task_id
        self.app_name = app_name
        self.port = port
        self.domain = domain
        self.env = env

    def task_exec(self):
        '''发布任务'''
        ret = dict(status=False,job_id=None,job_name=None)
        try:
            # jenkins开始调度发布
            obj = JenkinsAPI()
            print('start bulid ---> %s'%self.app_name)
            is_bulid = obj.check_is_build(self.app_name)
            if is_bulid:
                ret['log'] = '[%s]正在bulid中'%self.app_name
                raise Exception
            else:
                param_dict= {'domain': self.domain,'port': self.port,'namespace': self.env}
                print('param_dict->>>>>>>',param_dict)
                #job_id = obj.build_job(project_name)
                job_id = obj.build_job_param(self.app_name,param_dict)
                time.sleep(10)  #给jenkins10秒缓冲时间
                if job_id:
                    job_name = '%s #%s'%(self.app_name,job_id)
                    while True:
                        time.sleep(0.5)
                        check_status = obj.check_is_build(self.app_name)
                        self.task_log(job_id)
                        if not check_status:
                            self.flag = False
                            break

                    ret['status'] = True
                    ret['job_id'] = job_id
                    ret['job_name'] = job_name
                else:
                    ret['log'] = '任务提交失败'
                return ret
        except Exception as e:
            print('error-->>>')
            print(e)
            ret['log'] = 'bulid异常终止'
            return ret


    def task_log(self,job_id):
        log_dir = '%s/logs'%BASE_DIR
        cmd = 'wget -c -t 10 %s/job/%s/%s/consoleText  --user=%s --password=%s --auth-no-challenge -O ' \
              '%s/%s.log'%(jenkins_conf['url'],self.app_name,job_id,jenkins_conf['user'],
                           jenkins_conf['pwd'],log_dir,self.task_id)
        #print(cmd)
        exec_shell(cmd)