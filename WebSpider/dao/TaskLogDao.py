#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import time

from config import DB_SCHEAM
from datasource.DataConnUtil import DataConn


class TaskLogDao:
	'''
		负责日志新增更新dao
	'''
	#记录当前任务链执行情况
	def insertTaskLog(self,chainCode):
		execSql = r'''
			insert into ''' + DB_SCHEAM +r'''.SPIDER_TASK_LOG_TB values('{TASK_CHAIN_CODE}','progress','{UPDATE_TIME}','')
		'''
		currentDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

		return DataConn.execute(execSql, TASK_CHAIN_CODE=chainCode,UPDATE_TIME=currentDate);

	#更新日志
	def updateTaskLog(self,chainCode,status,reason):
		execSql = r'''
			update ''' + DB_SCHEAM +r'''.SPIDER_TASK_LOG_TB set EXEC_STATUS = '{EXEC_STATUS}',
			UPDATE_TIME = '{UPDATE_TIME}',TASK_REASON='{TASK_REASON}'
			where TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
		'''
		currentDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

		return DataConn.execute(execSql, TASK_CHAIN_CODE=chainCode,EXEC_STATUS=status,UPDATE_TIME=currentDate,TASK_REASON=reason);

	#查询日志是否存在
	def selectLog(self,chainCode):
		execSql = r'''
					select * from ''' + DB_SCHEAM +r'''.SPIDER_TASK_LOG_TB
					where TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
				'''
		logs = DataConn.executeQuery(execSql, TASK_CHAIN_CODE=chainCode);
		if len(logs) > 0:
			return logs[0]
		return None
	#记录日志
	def recodeLog(self,chainCode, status, reason):
		# 记录日志
		taskLog = self.selectLog(chainCode)
		if not taskLog:
			self.insertTaskLog(chainCode);
		else:
			reason += taskLog['TASK_REASON'] if taskLog['TASK_REASON'] and status != 'progress' else ''
			self.updateTaskLog(chainCode, status, reason);