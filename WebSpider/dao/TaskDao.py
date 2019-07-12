#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from config import DB_SCHEAM
from datasource.DataConnUtil import DataConn


class TaskDao:
	'''
		任务数据DAO
	'''
	#获取任务基本信息
	#任务编号
	#返回任务
	def getTask(self,taskCode):
		execSql = r'''
			select * from 
			''' + DB_SCHEAM +r'''
				.SPIDER_TASK_TB
				where TASK_STATUS = '1'
				and TASK_CODE = '{TASK_CODE}'
			'''
		taskList= DataConn.executeQuery(execSql,TASK_CODE=taskCode);
		if len(taskList)>0:
			return  taskList[0]
		return None

	#获取登录型任务
	def getLoginTask(self,chainCode):
		execSql = r'''
			select * from 
			''' + DB_SCHEAM +r'''
				.SPIDER_TASK_TB
				where TASK_STATUS = '1'
				and TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
				and TASK_TYPE ='login'
		'''
		taskList = DataConn.executeQuery(execSql, TASK_CHAIN_CODE=chainCode);
		if len(taskList) > 0:
			return taskList[0]
		return None
	#通过任务链查询任务信息（递归结构）
	#chainCode:任务链编号
	#返回任务结果集
	def  getTaskByChain(self,chainCode):
		execSql = r'''
			WITH
    TASK_TB(LEVE,TASK_CODE,
            TASK_NAME,
            TASK_STATUS,
            TASK_TYPE,
            TASK_CHAIN_CODE,
            BELONG_TASK_CODE,
            FORMAT_TYPE,
            FETCH_URL,
            UPLOAD_FALG,
            HEADER_CONTEXT,
            LOGIN_SUCESS_FLAG,
            REQUEST_METHOD,
            RESPONSE_METHOD,
            UPDATOR_CODE,
           UPDATE_TIME)AS 
    (
        SELECT
            1 ,
            a.TASK_CODE,
            A.TASK_NAME,
            A.TASK_STATUS,
            A.TASK_TYPE,
            A.TASK_CHAIN_CODE,
            A.BELONG_TASK_CODE,
            A.FORMAT_TYPE,
            A.FETCH_URL,
            A.UPLOAD_FALG,
            A.HEADER_CONTEXT,
            A.LOGIN_SUCESS_FLAG,
            A.REQUEST_METHOD,
            A.RESPONSE_METHOD,
            A.UPDATOR_CODE,
            A.UPDATE_TIME
        FROM
            ''' + DB_SCHEAM +r'''.SPIDER_TASK_TB a
        WHERE
            a.TASK_STATUS='1'
        AND a.BELONG_TASK_CODE IS NULL
        and a.TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
		UNION ALL
		SELECT
			LEVE+1,
			b.TASK_CODE,
			B.TASK_NAME,
			B.TASK_STATUS,
			B.TASK_TYPE,
			B.TASK_CHAIN_CODE,
			B.BELONG_TASK_CODE,
			B.FORMAT_TYPE,
			B.FETCH_URL,
			B.UPLOAD_FALG,
			B.HEADER_CONTEXT,
			B.LOGIN_SUCESS_FLAG,
            B.REQUEST_METHOD,
            B.RESPONSE_METHOD,
			B.UPDATOR_CODE,
			B.UPDATE_TIME
		FROM
			''' + DB_SCHEAM +r'''.SPIDER_TASK_TB b,
			TASK_TB a
		WHERE
			b.BELONG_TASK_CODE = a.TASK_CODE
			AND b.TASK_STATUS = '1')
		 SELECT * FROM TASK_TB where TASK_CHAIN_CODE='{TASK_CHAIN_CODE}'
		'''
		return DataConn.executeQuery(execSql,TASK_CHAIN_CODE=chainCode);

	#查询任务链层级数
	#chainCode:任务链编号
	#层级
	def getTaskChainLevel(self,chainCode):
		execSql = r'''
			WITH
    TASK_TB(LEVE,TASK_CODE,
            TASK_CHAIN_CODE,
            BELONG_TASK_CODE)AS 
    (
        SELECT
            1 ,
            a.TASK_CODE,
            A.TASK_CHAIN_CODE,
            A.BELONG_TASK_CODE
        FROM
            ''' + DB_SCHEAM +r'''.SPIDER_TASK_TB a
        WHERE
            a.TASK_STATUS='1'
        AND a.BELONG_TASK_CODE IS NULL
        AND TASK_CHAIN_CODE='{TASK_CHAIN_CODE}'
	UNION ALL
	SELECT
		LEVE+1,
		b.TASK_CODE,
		B.TASK_CHAIN_CODE,
		B.BELONG_TASK_CODE
	FROM
		''' + DB_SCHEAM +r'''.SPIDER_TASK_TB b,
		TASK_TB a
	WHERE
		b.BELONG_TASK_CODE = a.TASK_CODE
		AND b.TASK_STATUS = '1')
	 SELECT max(leve) FROM TASK_TB 
	 	where TASK_CHAIN_CODE='{TASK_CHAIN_CODE}'
		'''
		return DataConn.executeQuery(execSql, TASK_CHAIN_CODE=chainCode);



