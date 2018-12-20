#! /usr/bin/env python
# -*-coding:utf8-*-
# __author__ = 'ming'


def mixStr(pstr):
    if (isinstance(pstr, str)):
        return pstr
    else:
        return str(pstr)


class VmbException(Exception):
    # ===========================================================================
    # 业务异常类
    # ===========================================================================
    def __init__(self):
        self.errorcode = None
        self.message = None
        self.subcode = None
        self.submsg = None
        self.application_host = None
        self.service_host = None

    def __str__(self, *args, **kwargs):
        sb = "errorcode=" + mixStr(self.errorcode) + \
             " message=" + mixStr(self.message) + \
             " subcode=" + mixStr(self.subcode) + \
             " submsg=" + mixStr(self.submsg) + \
             " application_host=" + mixStr(self.application_host) + \
             " service_host=" + mixStr(self.service_host)
        return sb


class DataError(Exception):
    pass


class DataNotFoundError(Exception):
    pass


class ParamError(Exception):
    pass


class ConfigError(Exception):
    def __init__(self, config_key, *args, **kwargs):
        self.config_key = config_key
        super(ConfigError, self).__init__(*args, **kwargs)