# -*- coding: utf-8 -*-
import scrapy
from SinaSFNews.items import SinasfnewsItem

class BasicSpider(scrapy.Spider):
    name = 'basic'
    #allowed_domains = ['web']
    start_urls = ['http://news.sina.com.cn/sf/news/fzrd/2018-11-19/doc-ihmutuec1603964.shtml']#http://sifa.sina.com.cn/news/

    def parse(self, response):
        # title = Field()  # 新闻标题
        # time = Field()  # 新闻发布时间
        # content = Field()  # 新闻内容
        # tag = Field()  # 新闻关键字
        # origin = Field()  # 新闻来源,e.g.楚天都市报

        item = SinasfnewsItem()
        item['title'] = response.xpath('//h1[@class="main-title"]/text()').extract()
        item.time = response.xpath('//span[@class="date"]/text()').extract()
        item.content = response.xpath('//*[@id="artibody"]/text()').extract()
        item.tag = response.xpath('//*[@id="keywords"]/@date-wkey').extract()
        item.origin = response.xpath('//span[@class="source"]/text()').extract()
        # self.log("title: %s"% response.xpath('//h1[@class="main-title"]/text()').extract())#/html/body/div[3]/h1
        # self.log("time: %s"% response.xpath('//span[@class="date"]/text()').extract())
        # self.log("origin: %s" % response.xpath('//span[@class="source"]/text()').extract())
        # self.log("tag: %s" % response.xpath('//*[@id="keywords"]/@date-wkey').extract())
        # self.log("content: %s" % response.xpath('//*[@id="artibody"]/text()').extract())

