#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import logging

import jpype
from scrapy.cmdline import execute

from dao.DictMappingDao import DictMappingDao
from dao.TaskChainDao import TaskChainDao
from dao.TaskDao import TaskDao


def execTaskChain(chainCode):
	#获取任务链
	taskChainDao = TaskChainDao()
	taskChains = taskChainDao.getTaskChain(chainCode);
	for taskChain in taskChains:
		chainCode = taskChain.get('TASK_CHAIN_CODE');
		logging.warning("当前正在执行的任务链：[%s]%s"%(chainCode,taskChain.get('TASK_CHAIN_NAME')))
		#获取任务链下所有任务
		taskDao = TaskDao();
		taskList = taskDao.getTaskByChain(chainCode);

		#获取登录任务、第一链层任务
		loginTask = taskDao.getLoginTask(chainCode);
		firstTasks = []
		for task in taskList:
			parentTaskCode = task.get('BELONG_TASK_CODE');
			if loginTask and loginTask.get('TASK_CODE')==parentTaskCode:
				firstTasks.append(task)
			elif not loginTask and not parentTaskCode:
				firstTasks.append(task)

		#获取任务链下所有任务层级
		chainLevels = taskDao.getTaskChainLevel(chainCode)

		# 获取输入参数
		dictMappingDao = DictMappingDao();
		return {
			'taskList':taskList,
			'loginTask':loginTask,
			'firstTasks':firstTasks,
			'chainLevels':chainLevels,
			'inputParms':dictMappingDao.getInputDictByTaskChain(chainCode),
			'outputParams':dictMappingDao.getOutputDictByTaskChain(chainCode)
		}
	



#转换输入参数结构为深度结构
def converParams(paramList,dictcode):
	roots = []
	dictParams = {}
	for param in paramList:
		parent = param.get('BELONG_MAPPING_CODE')
		child = param.get('MAPPING_CODE')
		level = param.get('LEVE')
		paramObj = {child:param.get('MAPPING_VALUE')}
		if level == 1 :
			roots.append(child)
		if not parent:
			continue
		if parent in dictParams.keys():
			dictParams[parent][child]=param.get('MAPPING_VALUE')
		elif dictParams.get(child):
			dictParams[parent][child]= dictParams.get(child)
		else:
			dictParams[parent] = paramObj
	# for root in roots:
	# 	rootDict[root]=(dictParams.get(root))
	if dictcode in roots :
		return dictParams.get(dictcode)
	return None

