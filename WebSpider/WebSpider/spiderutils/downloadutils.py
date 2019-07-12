#!/usr/bin/env python
# _*_ coding:utf-8 _*_


import demjson
import time

from WebSpider.items import JobKeyValueItem, JobListItem


#深度遍历json并返回指定属性第一匹配上的字典对象
def json_all_dict(dict_obj,filter_code):
    filter_value = []
    if isinstance(dict_obj,dict) : #使用isinstance检测数据类型
        for temp_key in dict_obj:
            temp_value = dict_obj[temp_key]
            if temp_key == filter_code:
                return temp_value
            returnValue=json_all_dict(temp_value,filter_code)
            if returnValue:
                filter_value.append(returnValue) #自我调用实现无限遍历
        if len(filter_value)>0:
            return filter_value[0]
#根据配置方式（行存、列存）保存item，并输出给管道
def saveItem(isColumnSave,each,isJsonType,taskCode,outParam=None,output=None):
    if isColumnSave:
        item = JobKeyValueItem();
        paramType = outParam.get("MAPPING_TYPE")
        paramValue = outParam.get("MAPPING_VALUE")
        item['key'] = outParam.get("MAPPING_CODE")
        item['value'] = str(matchMappingType(each, paramType, paramValue, isJsonType)) if isJsonType \
                    else matchMappingType(each, paramType, paramValue, isJsonType).extract()
        item['taskCode'] = taskCode
        item['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        return item
    else:
        item = JobListItem();
        item['taskCode'] = taskCode
        item['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        item['values']=[]
        for outParam in output:
            if outParam.get("TASK_CODE") == taskCode and outParam.get("MAPPING_CODE") != 'root':
                paramType = outParam.get("MAPPING_TYPE")
                paramValue = outParam.get("MAPPING_VALUE")
                item['values']+=str(matchMappingType(each, paramType, paramValue, isJsonType)) if isJsonType \
                    else matchMappingType(each, paramType, paramValue, isJsonType).extract()
        return item

def matchMappingType(response,paramType,paramValue,isJsonType):
        if isJsonType :
            jsonObj = demjson.decode(response.body)
            return json_all_dict(jsonObj,paramValue)
        elif paramType == 'xpath':
            return response.xpath(paramValue)
        elif paramType == 'css':
            return response.css(paramValue)

