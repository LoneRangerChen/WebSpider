#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from config import DB_SCHEAM
from datasource.DataConnUtil import DataConn


class TaskChainDao:
	'''
		任务链信息获取DAO
	'''


	#获取正常状态的任务链
	#
	#返回任务链结果集
	def getTaskChainList(self):
		execSql = r'''
			select * from 
			''' + DB_SCHEAM +r'''.SPIDER_TASK_CHAIN_TB
				where STATUS = '1'
			'''
		return DataConn.executeQuery(execSql);

	#获取任务链信息
	def getTaskChain(self,chainCode):
		execSql = r'''
					select * from 
					''' + DB_SCHEAM + r'''
						.SPIDER_TASK_CHAIN_TB
						where STATUS = '1'
						AND TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
					'''
		return DataConn.executeQuery(execSql,TASK_CHAIN_CODE=chainCode);

if __name__ == '__main__':
	taskChainDao = TaskChainDao()
	taskChains = taskChainDao.getTaskChain('chain001');
	print(taskChains)


