# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import time

import scrapy
from scrapy.loader import ItemLoader

#ItemLoader数据分离，采用数据分离和提取两部分
#默认采用xpath css进行数据提取
#可以对一个数据使用多个数据处理函数
from scrapy.loader.processors import TakeFirst, MapCompose




class WebspiderItem(ItemLoader):

    #默认返回数据为列表，列表中当有一条数据
    # default_output_processor = TakeFirst()
    pass
def getCurrentTime(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', value)


class JobKeyValueItem(scrapy.Item):
    #属性值映射接受ITEM
    # define the fields for your item here like:
    # name = scrapy.Field()
    key = scrapy.Field();
    value = scrapy.Field();
    taskCode = scrapy.Field();
    updateTime = scrapy.Field(input_processor=MapCompose(getCurrentTime));#更新时间



class JobListItem(scrapy.Item):
    # 结果集接受ITEM
    # define the fields for your item here like:
    # name = scrapy.Field()
    taskCode = scrapy.Field();
    values = scrapy.Field();
    updateTime = scrapy.Field(input_processor=MapCompose(getCurrentTime));  # 更新时间

