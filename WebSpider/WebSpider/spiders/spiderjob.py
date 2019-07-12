# -*- coding: utf-8 -*-
import json
import logging

import demjson
import scrapy
import time

from scrapy import Request, FormRequest

from WebSpider.items import WebspiderItem, JobKeyValueItem, JobListItem
from WebSpider.spiderutils.downloadutils import json_all_dict, matchMappingType, saveItem
from WebSpider.task.TaskChainService import execTaskChain, converParams
from dao.TaskLogDao import TaskLogDao


class SpiderjobSpider(scrapy.Spider):
    """
        爬虫任务
    """
    name = 'spiderjob'

    def __init__(self,chainCode,browse,savetype):
        #初始化任务链参数
        taskConfigs = execTaskChain(chainCode)
        #链下任务
        self.tasks=taskConfigs.get("taskList")
        #任务链层级
        self.levels = taskConfigs.get("chainLevels")
        #登录任务
        self.logintask = taskConfigs.get("loginTask")
        # 第一链任务
        self.firstTasks = taskConfigs.get('firstTasks')
        #输入参数
        self.input = taskConfigs.get("inputParms")
        #输出参数
        self.output = taskConfigs.get("outputParams")
        self.browse = browse
        self.savetype=savetype
        self.chainCode=chainCode

        self.header = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        taskConfigs.clear()
        del taskConfigs

    def start_requests(self):
        if self.logintask:
            loginUrl = self.logintask.get("FETCH_URL");
            headerStr = self.logintask.get("HEADER_CONTEXT");
            if headerStr:
                self.header = demjson.decode(headerStr)
            meta = {'login': True}
            yield Request(loginUrl, callback=self.login, errback=self.err_parse, headers=self.header,meta=meta)
        else:
            # 第一链任务
            for taskbo in self.firstTasks:
                yield self.requestByMethod(taskbo)

    def parse(self, response):
        #递归解析页面结束
        if response.text=='':
            logging.debug('解析页面结束。。。')
            return None
        taskCode = response.meta['taskCode']
        taskType = response.meta['tasktype']

        isColumnSave = True if response.meta['formattpye'] == '01' else False
        isJsonType = True if response.meta['responseMethod'] == 'json' else False
        tasklog = TaskLogDao()
        try:
            #输出参数(root)
            rootParam = None
            for outParam in self.output:
                if outParam.get("TASK_CODE")==taskCode and outParam.get("MAPPING_CODE") == 'root':
                    paramType = outParam.get("MAPPING_TYPE")
                    paramValue =outParam.get("MAPPING_VALUE")
                    rootParam = matchMappingType(response, paramType, paramValue,isJsonType)
                    break;
            if rootParam:
                if isColumnSave:
                    for each in rootParam:
                        for outParam in self.output:
                            if outParam.get("TASK_CODE") == taskCode and outParam.get("MAPPING_CODE") != 'root':
                                yield saveItem(isColumnSave,each,isJsonType,taskCode,outParam=outParam)
                else:
                    for each in rootParam:
                        yield saveItem(isColumnSave,each,isJsonType,taskCode,output=self.output)
                #支持分页查询（遍历总页数）
                if taskType == 'page':
                    if self.browse != 'CHROME':
                        logging.warning('目前网络爬虫WEBSPIDER系统，分页查询自动遍历方式只支持在CHROME(谷歌浏览器)中运行。')
                        return
                    meta = response.meta
                    meta['next'] = True
                    for param in self.input:
                        if param.get("TASK_CODE") == taskCode and param.get('MAPPING_CODE') in ('start','end'):
                            meta[param.get('MAPPING_CODE')]=param.get('MAPPING_VALUE')
                    # 回调parse处理下一页的url
                    yield Request(response.url, callback=self.parse,meta=meta,dont_filter=True)
                if 'next' in response.meta:
                    logging.debug('继续分页。。。')
                    return
            else:
                logging.warning('任务号：%s,无返回数据处理' % taskCode)
            #获取下一任务
            for childTask in self.tasks:
                if childTask.get("BELONG_TASK_CODE") == taskCode:
                    yield self.requestByMethod(childTask)
        except Exception as e:
            message = '任务号【%s】出错：%s。'%(taskCode,e.__str__())
            tasklog.recodeLog(self.chainCode,'fail',message)



    def err_parse(self, response):
        #TODO 登录异常重试
        print(response)
        pass

    def login(self,response):
        inputLoginParams = []
        for param in self.input:
            if param.get("TASK_CODE") == self.logintask.get("TASK_CODE"):
                inputLoginParams.append(param)
        #TODO 是否有验证码
        meta = {'logintask': True}
        if self.browse=='HTML':
            yield FormRequest.from_response(response,formdata=converParams(inputLoginParams,'formdata'),
                                        callback=self.parse_login,meta=meta)
        else:
            yield Request(response.url, callback=self.parse_login, errback=self.err_parse, headers=self.header,meta=meta,dont_filter=True)
        inputLoginParams.clear()
        del inputLoginParams

    #判断登录是否成功
    def parse_login(self,response):
        succflag= self.logintask.get("LOGIN_SUCESS_FLAG")
        if not succflag or succflag in response.text or succflag in response.url :
            # 第一链任务
            for taskbo in self.firstTasks:
                yield self.requestByMethod(taskbo)
        else:
            logging.warning("登录任务：%s，地址：%s，登录失败，请检查"%(self.logintask.get("TASK_CODE"),self.logintask.get("FETCH_URL")))
            raise Exception("登录任务：%s，地址：%s，登录失败，请检查"%(self.logintask.get("TASK_CODE"),self.logintask.get("FETCH_URL")))


    #根据任务类型不同调用请求类
    def requestByMethod(self,taskbo):
        url = taskbo.get("FETCH_URL")
        isRefresh = False
        if not taskbo.get("FETCH_URL"):
            url =self.logintask.get("FETCH_URL") if self.logintask else self.tasks[0].get('FETCH_URL')
            isRefresh =True
        
        requestType = taskbo.get("REQUEST_METHOD")

        meta = {'taskCode': taskbo.get("TASK_CODE"),
                'responseMethod': taskbo.get("RESPONSE_METHOD"),
                # 输出结果格式化类型01列存 02行存
                'formattpye': taskbo.get("FORMAT_TYPE"),
                #登录login、分页page、抓取fetch、上传upload、下载download
                'tasktype':taskbo.get('TASK_TYPE'),
                'isRefresh' :isRefresh}

        if requestType == 'post':
            inputLoginParams = []
            for param in self.input:
                if param.get("TASK_CODE") == taskbo.get("TASK_CODE"):
                    inputLoginParams.append(param)
            return Request(url, callback=self.parse, errback=self.err_parse, method='POST',meta=meta, dont_filter=True,
                           body=demjson.encode(converParams(inputLoginParams, 'formdata')))
        else:
            return Request(url, callback=self.parse, errback=self.err_parse, meta=meta,dont_filter=True)
