#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from config import DB_SCHEAM
from datasource.DataConnUtil import DataConn


class DictMappingDao:
	'''
		字典参数映射dao
	'''
	def getOutputDictByTaskChain(self,chainCode):
		execSql = r'''
			SELECT
				a.MAPPING_CODE,
				A.MAPPING_TYPE,
				A.MAPPING_VALUE,
				A.BELONG_MAPPING_CODE,
				A.TASK_CODE
			FROM
				''' + DB_SCHEAM +r'''.SPIDER_DICT_MAPPING_TB a
			LEFT JOIN
				''' + DB_SCHEAM +r'''.SPIDER_TASK_TB b
			ON
				a.TASK_CODE=b.TASK_CODE
			where 
			a.INPUT_TYPE = 'out' and 
			b.TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
		'''
		return DataConn.executeQuery(execSql,TASK_CHAIN_CODE=chainCode);

	def getAllDictByTaskChain(self,chainCode):
		execSql = r'''
					SELECT
						a.MAPPING_CODE,
						A.MAPPING_TYPE,
						A.MAPPING_VALUE,
						A.BELONG_MAPPING_CODE,
						A.TASK_CODE,
						A.INPUT_TYPE,
						EXEC_ORDER
					FROM
						''' + DB_SCHEAM + r'''.SPIDER_DICT_MAPPING_TB a
					LEFT JOIN
						''' + DB_SCHEAM + r'''.SPIDER_TASK_TB b
					ON
						a.TASK_CODE=b.TASK_CODE
					where 
					b.TASK_CHAIN_CODE = '{TASK_CHAIN_CODE}'
					order by EXEC_ORDER
				'''
		return DataConn.executeQuery(execSql, TASK_CHAIN_CODE=chainCode);

	def getInputDictByTaskChain(self,chainCode):
		execSql = r'''
			WITH
				dict_param
				(
					leve,
					MAPPING_CODE,
					MAPPING_NAME,
					MAPPING_TYPE,
					MAPPING_VALUE,
					BELONG_MAPPING_CODE,
					TASK_CODE,
					INPUT_TYPE,
					EXEC_ORDER
				) AS
				(
					SELECT
						1,
						A.MAPPING_CODE,
						A.MAPPING_NAME,
						A.MAPPING_TYPE,
						A.MAPPING_VALUE,
						A.BELONG_MAPPING_CODE,
						A.TASK_CODE,
						A.INPUT_TYPE,
						A.EXEC_ORDER
					FROM
						''' + DB_SCHEAM +r'''.SPIDER_DICT_MAPPING_TB a
					LEFT JOIN
						''' + DB_SCHEAM +r'''.SPIDER_TASK_TB b
					ON
						a.TASK_CODE=b.TASK_CODE
					WHERE
						a.INPUT_TYPE IN ('in','click')
					AND a.BELONG_MAPPING_CODE IS NULL
					AND b.TASK_CHAIN_CODE ='{TASK_CHAIN_CODE}'
					UNION ALL
					SELECT
						a.leve+1,
						b.MAPPING_CODE,
						b.MAPPING_NAME,
						b.MAPPING_TYPE,
						b.MAPPING_VALUE,
						b.BELONG_MAPPING_CODE,
						b.TASK_CODE,
						b.INPUT_TYPE,
						b.EXEC_ORDER
					FROM
						dict_param a ,
						''' + DB_SCHEAM +r'''.SPIDER_DICT_MAPPING_TB b
					WHERE
						b.INPUT_TYPE IN ('in','click')
					AND b.BELONG_MAPPING_CODE=a.MAPPING_CODE
					and a.TASK_CODE = b.TASK_CODE
				)
			SELECT
				b.leve,
				b.MAPPING_CODE,
				B.MAPPING_NAME,
				B.MAPPING_TYPE,
				B.MAPPING_VALUE,
				B.BELONG_MAPPING_CODE,
				B.TASK_CODE,
				B.INPUT_TYPE,
				b.EXEC_ORDER
			FROM
				dict_param b
			ORDER BY
				leve DESC,b.EXEC_ORDER
		'''
		return DataConn.executeQuery(execSql, TASK_CHAIN_CODE=chainCode);