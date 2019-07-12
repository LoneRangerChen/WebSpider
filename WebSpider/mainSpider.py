#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
import time

import schedule

from dao.SmParamDao import SmParamDao


def start_spider():
	os.system('python run.py')
if __name__ == '__main__':
	print('开始检测，等待时间到达，开始执行')
	sm = SmParamDao()
	exect_time = sm.getDiffParamByCode('spiderschedule', 'None')[0]['PARAM_VALUE']
	print("定时器设置时间【%s】" % exect_time)
	taskJob = schedule.every().day.at(exect_time).do(start_spider)
	while True:
		params = sm.getDiffParamByCode('spiderschedule', exect_time)
		if len(params) > 0:
			exect_time = params[0]['PARAM_VALUE']
			schedule.cancel_job(taskJob)
			del taskJob
			taskJob = schedule.every().day.at(exect_time).do(start_spider)
			print("定时器设置时间已修改为【%s】" % exect_time)
		schedule.run_pending()
		time.sleep(20)
		