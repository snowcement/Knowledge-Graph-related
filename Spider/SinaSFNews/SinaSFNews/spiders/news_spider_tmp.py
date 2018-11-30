# -*- coding: utf-8 -*-
import scrapy
from SinaSFNews.items import SinasfnewsItem
from scrapy.loader.processors import MapCompose, Join   #处理器
from scrapy.loader import ItemLoader
import socket
import datetime
from scrapy.http import Request
import json
import re
from selenium import webdriver

#http://feed.mix.sina.com.cn/api/roll/get?pageid=354&lid=2120&num=30&versionNumber=1.2.8&page=1486&encode=utf-8&callback=feedCardJsonpCallback
MAX_PAGE = 1486 #大于MAX_PAGE时，返回结果为空
class NewsSpider(scrapy.Spider):
    name = 'sinawap'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://news.sina.com.cn/sf/news/fzrd/2018-11-23/doc-ihpevhck3225899.shtml']#https://sifa.sina.cn/2018-11-23/detail-ihpevhck2395501.d.html?from=wap
    #https://sifa.sina.cn/2018-11-22/detail-ihpevhck1218952.d.html?from=wap
    def parse(self, response):

        #网页分为电脑版和移动版，站点会根据用户的访问数据（user-agent）来决定返回给用户哪种网页
        if response.url in ['exception', '']:
            return
        loader = ItemLoader(item=SinasfnewsItem(), response=response)
        if response.url.endswith('wap'):#移动端
            loader.add_xpath('title', '//h1[@class="art_tit_h1"]/text()')
            loader.add_xpath('content', '//article[@class="art_box"]//p/text()', MapCompose(lambda x: x.strip()), Join('\t'))
            #wap中未包含tag,此处不添加
            loader.add_value('tag','')
            #wap中公众号发布的和非公众号发布的time,orgin提取方式不同
            sub = response.xpath('//figcaption[@class="weibo_detail"]').extract()
            if len(sub) > 0:#公众号
                loader.add_xpath('time', '//time[@class="weibo_time"]//*//text()', MapCompose(lambda x: x.strip()), Join('\t'))#只提取月日
                loader.add_xpath('origin', '//h2[@class="weibo_user"]/text()')
            else:#非公众号
                loader.add_xpath('time', '//time[@class="art_time"]/text()')
                loader.add_xpath('origin', '//cite[@class="art_cite"]/text()')
        else:#PC端
            # 1 http://news.sina.com.cn/sf/news/fzrd/2018-11-23/doc-ihpevhck3225899.shtml
            # 2 http://news.sina.com.cn/sf/news/2016-08-03/doc-ifxunyya3206505.shtml
            # tag title time origin均需要重新提取，格式变动
            title = response.xpath('//h1[@class="main-title"]/text()').extract()
            if len(title) > 0:  # 表示页面为第一种形式
                loader.add_xpath('title', '//h1[@class="main-title"]/text()')
                loader.add_xpath('time', '//span[@class="date"]/text()')
                loader.add_xpath('tag', '//*[@id="keywords"]//a/text()', MapCompose(lambda x: x.strip()), Join('\t'))
                loader.add_xpath('origin', '//span[@class="source"]/text()')
            else:
                loader.add_xpath('title', '//*[@id="artibodyTitle"]/text()')
                loader.add_xpath('time', '//*[@id="navtimeSource"]/text()', MapCompose(lambda x: x.strip()), Join(''))
                loader.add_xpath('origin', '//*[@id="navtimeSource"]//*/text()', MapCompose(lambda x: x.strip()),
                                 Join('\t'))
                loader.add_xpath('tag', '//*[@class="article-keywords"]//a/text()', MapCompose(lambda x: x.strip()),
                                 Join('\t'))
            loader.add_xpath('content', '//*[@id="artibody"]//p/text()', MapCompose(lambda x: x.strip()), Join('\t'))

        #管理字段
        loader.add_value('url', response.url)
        #无论是跳转到wap还是网页新闻均不受影响
        loader.add_value('project', self.settings.get('BOT_NAME'))
        loader.add_value('spider', self.name)
        loader.add_value('server', socket.gethostname())
        loader.add_value('date', datetime.datetime.now())

        #loader.add_xpath('next','//*[@id="feedCardContent"]//span[@class=next5]/a')
        return loader.load_item()