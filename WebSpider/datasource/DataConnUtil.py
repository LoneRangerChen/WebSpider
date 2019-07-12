#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import logging
import os

import jpype

#获取数据库连接
import config
from datasource.DataType import convent_data_type, database

class DataConn:
	@staticmethod
	def getConnect():
		envtup=DataConn.init__env_();
		jvm_arg = "-Djava.class.path=%s"% os.path.join(os.path.dirname(os.path.realpath(__file__)),'../lib/')+envtup[0]
		if not jpype.isJVMStarted():
			jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",jvm_arg)
		if not jpype.isThreadAttachedToJVM():
			jpype.attachThreadToJVM()

		try:
			# driver =JPackage("oracle.jdbc").OracleDriver();

			driverClass =jpype.JClass(envtup[1]);
			driver = driverClass()
			jpype.java.sql.DriverManager.deregisterDriver(driver);

			connect = jpype.java.sql.DriverManager.getConnection(config.URL, config.USER_NAME, config.PASSWORD);
			logging.debug("getConnect():获取连接成功")
			return connect;
		except Exception as expection:
			print(expection)
			print("getConnect():获取连接失败，请重试")

	#执行查询语句返回结果集
	@staticmethod
	def  executeQuery(sql,**kwargs):
		connect, statement, rs = None,None,None;
		try:
			if not sql or sql.isspace():
				print("executeQuery():执行SQL为空，请检查")
				return ;
			connect = DataConn.getConnect()
			statement = connect.createStatement();
			if kwargs:
				sql=sql.format(**kwargs);
			logging.debug("executeQuery():执行语句-->"+sql)
			resultSet = statement.executeQuery(sql);
			metaData = resultSet.getMetaData()
			columns = metaData.getColumnCount();
			rsultList=[];
			while resultSet.next():
				resultDict = {};
				for i in range(columns):
					columnName = metaData.getColumnName(i + 1);
					colValue=resultSet.getObject(i + 1);
					resultDict[columnName]=convent_data_type(colValue);
				rsultList.append(resultDict);
			return rsultList;
		except jpype.JException() as exception:
			exception.stacktrace
		finally:
			if rs:
				rs.close();
			if statement:
				statement.close();
			if connect:
				connect.close();


	#执行操作语句，返回执行成功数
	@staticmethod
	def execute(sql,**kwargs):
		connect,statement,rs= None,None,None;
		try:
			if not sql or sql.isspace():
				print("execute():执行SQL为空，请检查")
				return ;
			if ";" in sql :
				return DataConn.executeBatch(sql,**kwargs)
			connect = DataConn.getConnect()
			statement = connect.createStatement();
			if kwargs:
				sql=sql.format(**kwargs);
			logging.debug("execute():执行语句-->" + sql)
			resultSet = statement.executeUpdate(sql);
			return resultSet;
		except jpype.JException() as exception:
			exception.stacktrace
		finally:
			if rs:
				rs.close();
			if statement:
				statement.close();
			if connect:
				connect.close();
		
	# 执行操作语句，返回执行成功数
	@staticmethod
	def executeByConn(connect,sql, kwargs):
		statement, rs = None, None;
		try:
			if not sql or sql.isspace():
				logging.debug("execute():执行SQL为空，请检查")
				return;
			if ";" in sql:
				logging.debug("execute():执行SQL带有';'号，请检查")
				return
			statement = connect.createStatement();
			if kwargs:
				sql = sql.format(**kwargs);
			logging.debug("execute():执行语句-->" + sql)
			resultSet = statement.executeUpdate(sql);
			return resultSet;
		except jpype.JException() as exception:
			exception.stacktrace
		finally:
			if rs:
				rs.close();
			if statement:
				statement.close();
	#批量执行语句
	@staticmethod
	def executeBatch(sql,**kwargs):
		if kwargs:
			sql = sql.format(**kwargs);
		logging.debug("executeBatch():执行语句-->" + sql)
		sqls = str(sql).split(";")
		connect = DataConn.getConnect()
		statement = connect.createStatement();
		for execSql in sqls :
			if execSql :
				statement.addBatch(execSql);

		return statement.executeBatch();

	#初始化执行环境
	@staticmethod
	def init__env_():
		if config.DATA_BASE== database.ORACLE.value:
			return ("ojdbc6.jar","oracle.jdbc.OracleDriver")


if __name__ == '__main__':
	# logging.debug(execute("insert into crwm3.SM_USER_BAK(user_code) values('32312313')"));
	logging.debug(DataConn.executeQuery("select * from crwm3.SM_ORG_TB WHERE ORG_CODE = '{ORG_CODE}'",ORG_CODE='10'))
	jpype.shutdownJVM()

	# SQL="select * from crwm3.SM_ORG_TB WHERE ORG_CODE LIKE '%{ORG_CODE}%'".format(ORG_CODE=10);
	# logging.debug(SQL)

