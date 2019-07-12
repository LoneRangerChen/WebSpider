#!/usr/bin/env python
# _*_ coding:utf-8 _*_

#WINDOWS环境
#数据连接配置
#
#数据连接层连接地址、方式等
#数据库 oracle mysql h2 impala hive spark
DATA_BASE = 'oracle'
#数据库连接url 用户密码
URL = 'jdbc:oracle:thin:@172.1.3.28:1521:orcl'
USER_NAME = 'sunedp'
PASSWORD = 'sunedp'
#支撑jpype允许的JVM路径
JDK_JVM = 'C:\\Program Files\\Java\\jdk1.7.0_79\\jre\\bin\\server\\jvm.dll'
#数据库scheam
DB_SCHEAM = 'sunedp'



# 浏览器路径
CHROME_PATH = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'  # 可以指定绝对路径，如果不指定的话会在$PATH里面查找
CHROME_DRIVER_PATH = r'F:\产品\工具类产品\网络爬虫\01开发工具\chromedriver_win32\chromedriver.exe'  # 可以指定绝对路径，如果不指定的话会在$PATH里面查找


#useragent.json请求头库
USER_AGENT_PATH=r'WebSpider\user_agent.json'

#下载文件存储地址
DOWNLOAD_PATH=r"F:\迅雷下载"




#Linux环境
#数据连接配置
#
#数据连接层连接地址、方式等

#数据库 oracle mysql h2 impala hive spark
# DATA_BASE = 'oracle'
# #数据库连接url 用户密码
# URL = 'jdbc:oracle:thin:@172.1.3.28:1521:orcl'
# USER_NAME = 'sunedp'
# PASSWORD = 'sunedp'
# #支撑jpype允许的JVM路径
# JDK_JVM = '/usr/local/java/jdk1.7.0_79/jre/bin/java_vm'
# #数据库scheam
# DB_SCHEAM = 'sunedp'
#
#
#
# # 浏览器路径
# CHROME_PATH = r'/opt/google/chrome/chrome'  # 可以指定绝对路径，如果不指定的话会在$PATH里面查找
# CHROME_DRIVER_PATH = r'/opt/web/chromedriver'  # 可以指定绝对路径，如果不指定的话会在$PATH里面查找
#
#
# #useragent.json请求头库
# USER_AGENT_PATH=r'WebSpider/user_agent.json'
#
# #下载文件存储地址
# DOWNLOAD_PATH=r"/tmp"