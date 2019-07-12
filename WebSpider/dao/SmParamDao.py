#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from config import DB_SCHEAM
from datasource.DataConnUtil import DataConn


class SmParamDao:
	'''
		根据参数编号获取参数(参数值变化时有返回结果)
	'''
	def getDiffParamByCode(self,param_code,param_value):
		execSql = r'''
			select * from
			''' + DB_SCHEAM +r'''.SM_PARAM_TB
				where PARAM_CODE = '{param_code}'and  PARAM_VALUE != '{param_value}'
			'''.format(param_code=param_code,param_value=param_value)
		return DataConn.executeQuery(execSql);