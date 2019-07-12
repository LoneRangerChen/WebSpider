#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from scrapy.commands import ScrapyCommand


class Command(ScrapyCommand):
	requires_project = True
	
	def syntax(self):
		return '[options]'
	
	def short_desc(self):
		return 'Runs all of the spiders'
	
	def run(self, args, opts):
		self.crawler_process.crawl('spiderjob', **opts.__dict__)
		self.crawler_process.start()