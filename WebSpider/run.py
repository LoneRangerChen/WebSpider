#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import logging
import os
import sys
import time

import jpype
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
#记录日志
from dao.TaskChainDao import TaskChainDao
from dao.TaskLogDao import TaskLogDao

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


#启动爬虫
def start_spider():
	#获取任务链
	taskChainDao = TaskChainDao()
	taskChains = taskChainDao.getTaskChainList();
	tasklog=TaskLogDao()
	
	try:
		setting = get_project_settings()
		process = CrawlerProcess(setting)
		for taskChain in taskChains:
			chainCode = taskChain.get("TASK_CHAIN_CODE")
			#CHROME、HTML
			browseFlag =  taskChain.get("TASK_CHAIN_RENDERER")
			#sql保存到数据库 file只记录文件
			saveType = taskChain.get("OUTPUT_TYPE")
			logging.warning(
				"开始执行任务链：[%s]%s，调动爬虫程序scrapy crawl %s ，并记录日志" % (chainCode, taskChain.get('TASK_CHAIN_NAME'), 'commonspider'))
			#记录日志
			tasklog.recodeLog(chainCode,'progress','')
			process.crawl('spiderjob',chainCode=chainCode,browse=browseFlag,savetype=saveType)
			tasklog.recodeLog(chainCode, 'success','')
		process.start(stop_after_crawl=True)
		
	except Exception as e:
		logging.error('爬虫程序--出现错误--',e)
	finally:
		jpype.shutdownJVM()
		process.stop()
		del process
		kill_CHROME_IDS('chrome')
		
#清理chrome进程(LINUX环境)
def kill_CHROME_IDS(process_name):
	if sys.platform=='linux':
		ids = os.popen("ps -ef | grep '%s'| grep -v '$0'| grep -v 'grep' | awk '{print $2}'"%process_name)
		for idtmp in ids.readlines():
			os.system('kill -9 %s' % idtmp)
		ids.close()
	
if __name__ == '__main__':
	start_spider()

