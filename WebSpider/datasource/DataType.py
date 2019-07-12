#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#根据类型typeIndex下标，换化结果值成对应python类型
from enum import Enum

import jpype

#转化java类型为内置类型
def convent_data_type(value):
	if not value :
		return None
	#java.math.BigDecimal
	if type(value) == jpype.java.math.BigDecimal:
		floatValue=float(value.doubleValue())
		return int(value.doubleValue()) if floatValue.is_integer() else floatValue

	#java.sql.Timestamp
	elif type(value) == jpype.java.sql.Timestamp:
		return str(value)
	# oracle.sql.Timestamp
	elif str(type(value)) == "<class 'jpype._jclass.oracle.sql.TIMESTAMP'>":
		return str(value)
	# java.sql.Date
	elif type(value) == jpype.java.sql.Date:
		return str(value)
	else :
		return value

class database(Enum):
	'''
		支持的数据库类型 oracle
	'''
	ORACLE = 'oracle'
