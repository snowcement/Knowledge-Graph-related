# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class SinasfnewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    #Primary fields
    title = Field()#新闻标题
    time = Field()#新闻发布时间
    content = Field()#新闻内容
    tag = Field()#新闻关键字
    origin = Field()#新闻来源,e.g.楚天都市报
    #Housekeeping fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()