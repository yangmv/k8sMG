#!/usr/bin/env python
# -*-coding:utf-8-*-

import time
from libs.web_logs import ins_log
from libs.mqhelper import MessageQueueBase
from libs.db_context import DBContext
from models.project import Publish,Task
from app.tasks.exec_list.publish import TaskPublish
from datetime import datetime
import threading

class DealMQ(MessageQueueBase):
    """接受MQ消息 根据订单ID和分组 多线程执行任务"""

    def __init__(self):
        super(DealMQ, self).__init__(exchange='task_sced', exchange_type='direct', routing_key='the_task',
                                     queue_name='deal_task_sched', no_ack=False)
    def on_message(self, body):
        print('[on_message]')
        #return 1
        #body消息内容,内容为 [task ID]
        ins_log.read_log('info', 'flow_id is {}'.format(body))
        flow_id = int(body)

        with DBContext('readonly') as session:
            status = session.query(Publish).filter(Publish.id == flow_id).first().status
            print(status)

        if status == '0':
            self.exec_task(flow_id,'qa')
            ####### while循环监控,若status=2,则表示审核通过,开始执行正式
            print('[test环境ok]')
            with DBContext('readonly') as session:
                dev_status = session.query(Publish).filter(Publish.id == flow_id).first()
                if not dev_status:
                    #如果测试环境没执行成功,则不会往下执行
                    print('test not ok...')
                    return False
        elif status == '12' or status == '2':
            pass
        else:
            print('任务已经执行过')
            return

        int_sleep, end_sleep = 1, 1
        while True:
            ### 挂起的任务设置休眠时间
            ins_log.read_log('info', 'The task-{0} is not ready, retry after {1} s of sleep'.format(flow_id, int_sleep))
            time.sleep(int_sleep)
            int_sleep += 2
            end_sleep += int_sleep
            if int_sleep > 15: int_sleep = 15
            with DBContext('readonly') as session:
                check_status = session.query(Publish).filter(Publish.id == flow_id, Publish.status == '2').first()
            #status==2,那么继续循环并sleep任务,直到任务被接手
            if check_status:break
            if end_sleep > 150:raise SystemExit('message timeout')

        #开始发正式环境
        print('start release......')
        self.exec_task(flow_id,'release')
        print('[release环境ok]')



    def exec_task(self, flow_id ,env):
        def exec_task(app,env_id):
            print('app--->',app)
            with DBContext('default') as session:
                task_obj = Task(
                    publish_id = flow_id,
                    env_id = env_id,
                    app_id = app.id,
                    start_exe_time = datetime.now()
                )
                session.add(task_obj)
                session.commit()

                print('start exec....')
                domain = 'qa-%s.%s'%(app.name,'yangmv.com') if env == 'qa' else '%s.%s'%(app.name,'yangmv.com')
                tasks = TaskPublish(task_obj.id,app.name,app.port,domain,env)
                job_ret = tasks.task_exec()
                if job_ret['status']:
                    print('ok')
                    task_obj.job_id = job_ret['job_id']
                    task_obj.name = job_ret['job_name']
                    task_obj.status = '1'
                    task_obj.end_exe_time = datetime.now()
                else:
                    print('no ok')
                    task_obj.status = '0'
                    task_obj.logs = job_ret['log']
                    lock.acquire()  # 加锁
                    Error_TAG.append(task_obj.id)
                    lock.release()  # 开锁
                session.commit()

        with DBContext('default') as session:
            #更新发布表状态,标记状态为11执行中
            publish = session.query(Publish).filter(Publish.id == flow_id).first()
            publish.status = '11' if env == 'qa' else '31'
            session.commit()

            #获取发布所有app
            all_app = publish.app
            env_id = 1 if env == 'qa' else 3 #1为测试,3为正式
            print('all_app------>',all_app)

            Error_TAG = []
            lock = threading.Lock()
            threads = [threading.Thread(target=exec_task, args=(app,env_id,)) for app in all_app]
            for start_t in threads:
                start_t.start()
            for join_t in threads:
                join_t.join()

            if Error_TAG:
                publish.status = '13' if env == 'qa' else '33'   #本项目测试/正式环境下面有一个或多个APP未成功发布
            else:
                publish.status = '12' if env == 'qa' else '32'  #本项目测试/正式环境下面所有APP均成功发布
            session.commit()


    def exec_task22(self, flow_id):
        '''
            开始执行任务
            0 为等审核
            1 审核通过,待执行,任务接手后状态为标记为2
            2 正在执行
        '''
        ### 如果任务没有审批，则进入休眠,初始休眠时间为0秒
        int_sleep, end_sleep = 1, 1
        while True:
            ### 挂起的任务设置休眠时间
            ins_log.read_log('info', 'The task-{0} is not ready, retry after {1} s of sleep'.format(flow_id, int_sleep))
            time.sleep(int_sleep)
            int_sleep += 2
            end_sleep += int_sleep
            if int_sleep > 15: int_sleep = 15
            with DBContext('readonly') as session:
                status = session.query(Publish).filter(Publish.id == flow_id, Publish.status == '0').first()
            #status==0,那么继续循环并sleep任务,直到任务被接手
            if not status:break     #任务状态!=new,比如ready,那么就开始退出循环,开始执行
            if end_sleep > 150:raise SystemExit('message timeout')

        ### 审核通过,现在开始执行,标记状态为2
        with DBContext('default') as session:
            session.query(Publish).filter(Publish.id == flow_id).update({Publish.status: '2',
                                                                         Publish.start_exe_time: datetime.now()})
            session.commit()
        print('start exec....')
        task = TaskPublish(flow_id)
        task.task_exec()




if __name__ == "__main__":
    pass
