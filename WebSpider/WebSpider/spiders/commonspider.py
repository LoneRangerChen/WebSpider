# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy import Request, FormRequest

from WebSpider.items import WebspiderItem, JobKeyValueItem


class CommonspiderSpider(scrapy.Spider):
    """
        爬虫任务链入口
    """
    name = 'commonspider'

    def __init__(self, value=''):
        # self.value = value
        self.start_urls =['http://115.236.66.162:9043/zentao/index.php?m=project&f=bug&projectID=28']
        self.header = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }

    def start_requests(self):
        url = 'http://115.236.66.162:9043/zentao/index.php?m=user&f=login&referer=L3plbnRhby9pbmRleC5waHA='
        yield Request(url, callback=self.login, errback=self.err_parse, headers=self.header)

    def parse(self, response):

        item_loader = WebspiderItem(item=JobKeyValueItem(),selector=response.xpath('//*[@id="bugList"]/tbody/tr[*]'))

        item_loader.add_value("key","bug标题")
        item_loader.add_xpath("value",'td[4]/a/text()')
        item_loader.add_value("updateTime",(time.localtime(),))

        #收集并保存每一个field的数据，并传送给管道
        item = item_loader.load_item()
        yield item





    def err_parse(self, response):
        pass

    def login(self,response):
        formdata = {
             "account": 'chen.fei',
            "password": 'Cf123456',
            "referer" : 'http://115.236.66.162:9043/zentao/index.php?m=user&f=logout'}
        yield FormRequest.from_response(response,formdata=formdata,
                                        callback=self.parse_login)
    def parse_login(self,response):
        if "/zentao/index.php?m=index&f=index" in response.text :
            yield from super().start_requests()