# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging

import demjson

from WebSpider.items import  JobListItem
from config import DB_SCHEAM
from datasource.DataConnUtil import DataConn


class WebspiderPipeline(object):
    def __init__(self):
        logging.info('spider start write......................')
        self.connect=DataConn.getConnect()
        self.taskcode=''
        pass
    
    def process_item(self, item, spider):
        self.taskcode = spider.chainCode
        if spider.savetype == 'sql':
            insertItem = {'taskCode': item['taskCode'], 'updateTime': item['updateTime']}
            insertSql = r'''
                INSERT INTO
                ''' + DB_SCHEAM + r'''.SPIDER_RESULT_KV_TB(TASK_CODE,RESULT_NAME,RESULT_VALUE,UPDATE_TIME)
                VALUES ('{taskCode}','{key}','{value}','{updateTime}')
            '''
            if type(item) == JobListItem:
                columnSql=''
                valueSql=""
                for itm in range(len(item['values'])):
                    colustr = 'COLUMN_'+str(itm+1)
                    columnSql+=colustr+','
                    valueSql +="'{"+colustr+"}',"
                    insertItem[colustr]=item['values'][itm]
                insertSql = r'''INSERT INTO
                                    ''' + DB_SCHEAM + r'''.SPIDER_RESULT_LIST_TB(TASK_CODE,'''+columnSql+'''UPDATE_TIME)
                                    VALUES ('{taskCode}','''+valueSql+''''{updateTime}')
                                '''
            else:
                insertItem["key"] = item['key']
                insertItem["value"] = item['value']
            DataConn.executeByConn(self.connect,insertSql,insertItem)
        return insertItem
    
    def __del__(self):
        print('taskchain["%s"]:spider end write.....'%self.taskcode)
        if self.connect:
            self.connect.close();
        pass