#!/usr/bin/env python
#encoding:utf-8
import fire
from tornado.options import define
from settings import app_settings
from app.mg.applications import Application as MgApp
from app.tasks.program import Application as DealApp
from app.ws.applications import Application as WsApp

define("service", default='api', help="start service flag", type=str)
class My():
    def __init__(self,service):
        if service == 'mg':
            self.app = MgApp(**app_settings)
        elif service == 'exec_task':
            self.app = DealApp(**app_settings)
        elif service == 'ws':
            self.app = WsApp(**app_settings)
        self.app.start_server()

if __name__ == '__main__':
    fire.Fire(My)