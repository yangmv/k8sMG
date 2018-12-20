#!/usr/bin/env python
#encoding:utf-8
from libs.application import Application as myapplication
from app.ws.handlers.index_handler import index_urls

import tornado
from app.ws.handlers.index_handler import stdout_file,tail_file
from libs.web_logs import ins_log

class Application(myapplication):
    def __init__(self,**settings):
        urls = []
        urls.extend(index_urls)
        tailed_callback = tornado.ioloop.PeriodicCallback(tail_file, 5)
        tailed_callback.start()
        super(Application,self).__init__(urls,**settings)


    def start_server(self):
        try:
            ins_log.read_log('info', 'web wocket start sucessfuled.')
            self.io_loop.start()
        except KeyboardInterrupt:
            self.io_loop.stop()
            stdout_file.close()
        except:
            import traceback
            ins_log.read_log('error', '%(tra)s'% dict(tra=traceback.format_exc()))

if __name__ == '__main__':
    pass