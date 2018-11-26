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
CURRENT_PAGENUM = 0
class NewsSpider(scrapy.Spider):
    name = 'sinasf'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://feed.mix.sina.com.cn/api/roll/get?pageid=354&lid=2120&num=30&versionNumber=1.2.8&page=1&encode=utf-8&callback=feedCardJsonpCallback']#http://sifa.sina.com.cn/news/ http://news.sina.com.cn/sf/news/fzrd/2018-11-19/doc-ihmutuec1603964.shtml
    #日志记录当前爬取条数
    def __init__(self):
        super(NewsSpider, self).__init__()
        self.file = open('log_crawl.txt', mode='a+', encoding='utf-8')
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    #     }
    def __del__(self):
        self.file.close()

    def parse(self, response):
        responsestr = response.text.replace('try{feedCardJsonpCallback(', '').replace(');}catch(e){};', '')
        if responsestr.strip() != '':
            dict = json.loads(responsestr)
            result = dict['result']
            data = result['data']
            for meta in data:
                url = meta['url']  # wapurl为在移动端显示的新闻url
                yield Request(url, callback=self.parse_item)  # , headers=self.headers

            # 提取连接中page信息，并将当前页更新
            page_info = re.search(r'(page=[1-9][0-9]*)', response.url).group(1)
            page_num = int(page_info[5:])
            if page_num < MAX_PAGE:
                page_num += 1
                page_info_new = 'page=' + str(page_num)
                next_url = re.sub(r'(page=[1-9][0-9]*)', page_info_new, response.url)
                # print("next_url: %s" % next_url)
                # 处理链接
                meta = {
                    'download_timeout': 15
                }
                yield Request(next_url, dont_filter=True, meta=meta)  # , headers=self.headers

    def parse_item(self, response):
        '''
        This function parses a property page.
        @url http://news.sina.com.cn/sf/news/fzrd/2018-11-19/doc-ihmutuec1603964.shtml
        @returns items 1
        @scrapes title time content tag origin
        @scrapes url project spider server date
        '''

        # content = response.xpath('//*[@id="artibody"]//p/text()').extract()
        # for index in range(len(content)):
        #     content[index] = content[index].strip()#去除\u3000等空白符
        # content = '\t'.join(content)
        # self.log("title: %s"% response.xpath('//h1[@class="main-title"]/text()').extract()[0])#/html/body/div[3]/h1
        # self.log("time: %s"% response.xpath('//span[@class="date"]/text()').extract()[0])
        # self.log("origin: %s" % response.xpath('//span[@class="source"]/text()').extract()[0])
        # self.log("tag: %s" % response.xpath('//*[@id="keywords"]//a/text()').extract())#标签列表
        # self.log("content: %s" % content)

        # item = SinasfnewsItem()
        # item['title'] = response.xpath('//h1[@class="main-title"]/text()').extract()[0]
        # item['time'] = response.xpath('//span[@class="date"]/text()').extract()[0]
        # item['content'] = content
        # item['tag'] = response.xpath('//*[@id="keywords"]//a/text()').extract()
        # item['origin'] = response.xpath('//span[@class="source"]/text()').extract()[0]
        # return item
        global CURRENT_PAGENUM
        CURRENT_PAGENUM += 1
        self.file.write('Current parsing the %s th page\n' % CURRENT_PAGENUM)
        self.file.flush()
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
            if len(sub) > 0:  # 公众号
                loader.add_xpath('time', '//time[@class="weibo_time"]//*//text()', MapCompose(lambda x: x.strip()),
                                 Join('\t'))  # 只提取月日
                loader.add_xpath('origin', '//h2[@class="weibo_user"]/text()')
            else:#非公众号
                loader.add_xpath('time', '//time[@class="art_time"]/text()')
                loader.add_xpath('origin', '//cite[@class="art_cite"]/text()')
        else:#PC端
            #1 http://news.sina.com.cn/sf/news/fzrd/2018-11-23/doc-ihpevhck3225899.shtml
            #2 http://news.sina.com.cn/sf/news/2016-08-03/doc-ifxunyya3206505.shtml
            #tag title time origin均需要重新提取，格式变动
            title = response.xpath('//h1[@class="main-title"]/text()').extract()
            if len(title) > 0:  # 表示页面为第一种形式
                loader.add_xpath('title', '//h1[@class="main-title"]/text()')
                loader.add_xpath('time', '//span[@class="date"]/text()')
                loader.add_xpath('tag', '//*[@id="keywords"]//a/text()', MapCompose(lambda x: x.strip()), Join('\t'))
                loader.add_xpath('origin', '//span[@class="source"]/text()')
            else:
                loader.add_xpath('title', '//*[@id="artibodyTitle"]/text()')
                loader.add_xpath('time', '//*[@id="navtimeSource"]/text()', MapCompose(lambda x: x.strip()), Join(''))
                loader.add_xpath('origin', '//*[@id="navtimeSource"]/span/text()', MapCompose(lambda x: x.strip()),
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


