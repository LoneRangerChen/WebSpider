#!/usr/bin/env python
# _*_ coding:utf-8 _*_

#模拟登录工具
#

from scrapy import FormRequest


'''
传统的登录方式

'''
def basic_login(response,formdata,callback,type ='post'):
	yield FormRequest.from_response(response, formdata=formdata, callback=callback)





