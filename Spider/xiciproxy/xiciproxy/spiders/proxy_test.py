# -*- coding: utf-8 -*-
import scrapy
import json
import pprint
class AnythingSpider(scrapy.Spider):
    name = 'anything'
    allowed_domains = ['httpbin.org']
    start_urls = ['http://httpbin.org/anything']

    def parse(self, response):
        ret = json.loads(response.text)
        pprint.pprint(ret)