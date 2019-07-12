#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import random

#伪装头部信息骗过网站的防爬策略
class User_Agent(object):
	
	def __init__(self, json_file="user_agent.json"):
		"""
		:param json_file: 下载后内容保存的文件
		"""
		self.json_file = json_file
		self.ua_data = self.user_agent_data().get("browsers")
		self.b = ['chrome', 'opera', 'firefox', 'safari', 'internetexplorer']
		# -------
		self.chrome = lambda: random.choice(self.ua_data.get("chrome"))
		self.opera = lambda: random.choice(self.ua_data.get("opera"))
		self.firefox = lambda: random.choice(self.ua_data.get("firefox"))
		self.safari = lambda: random.choice(self.ua_data.get("safari"))
		self.ie = lambda: random.choice(self.ua_data.get("internetexplorer"))
		self.random = lambda: random.choice(self.ua_data.get(random.choice(self.b)))
	
	def user_agent_data(self):
		with open(self.json_file, "r") as fp:
			data = fp.read()
		return json.loads(data)

