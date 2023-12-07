#!/usr/bin/env python
#encoding:utf-8
'''
@author: yangmv
@file: test.py
@time: 18/11/7下午4:33
'''
import jenkins
from settings import jenkins_conf as conf
import requests
from requests.auth import HTTPBasicAuth

class JenkinsAPI():
    def __init__(self):
        # self.url = 'http://212.64.39.210:30002'
        # self.user = 'admin'
        # self.pwd = '123456'
        self.url = conf['url']
        self.user = conf['user']
        self.pwd = conf['pwd']
        self.server = jenkins.Jenkins(self.url, username=self.user, password=self.pwd)

    def get_version(self):
        self.server.get_whoami()
        version = self.server.get_version()
        print(version)

    def get_job_info(self,job_name):
        '''获取Job相关信息'''
        ret = self.server.get_job_info(job_name)
        return ret

    def get_job_id(self,job_name):
        ret = self.server.get_job_info(job_name)
        return ret['nextBuildNumber']

    def get_build_info(self,job_name,build_number):
        '''获取job指定构建信息'''
        ret = self.server.get_build_info(job_name,build_number)
        #print(json.dumps(ret))
        return ret


    def check_is_build(self,job_name):
        '''检查项目是否正在build'''
        try:
            last_build = self.get_job_info(job_name)['lastBuild']
            if last_build:
                last_build = int(last_build['number'])
                ret = self.get_build_info(job_name,last_build)
                return ret['building']
            else:
                return False
        except Exception as e:
            print('check_is_build [error]-->',e)
            return True

    def build_job(self,job_name):
        '''构建指定job'''
        try:
            self.server.build_job(job_name)
            job_id = self.get_job_id(job_name)
        except Exception as e:
            print(e)
            job_id = None
        return job_id

    def build_job_param(self,job_name,data):
        '''构建带参数的job'''
        try:
            self.server.build_job(job_name,parameters=data)
            job_id = self.get_job_id(job_name)
        except Exception as e:
            print(e)
            job_id = None
        return job_id

    def get_job_log(self,job_name,job_id):
        '''获取job console 日志'''
        auth = HTTPBasicAuth(self.user,self.pwd)
        ret = requests.get(url='%s/job/%s/%s/consoleText'%(self.url,job_name,job_id),auth=auth)
        return ret.text

if __name__ == '__main__':
    obj = JenkinsAPI()
    obj.check_is_build('codo-cmdb')
