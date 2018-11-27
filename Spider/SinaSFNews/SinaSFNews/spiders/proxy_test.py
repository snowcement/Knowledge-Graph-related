# -*- coding: utf-8 -*-
import scrapy
import json
import pprint
# class AnythingSpider(scrapy.Spider):
# #     name = 'anything'
# #     allowed_domains = ['httpbin.org']
# #     start_urls = ['http://httpbin.org/anything']
# #
# #     def parse(self, response):
# #         ret = json.loads(response.text)
# #         pprint.pprint(ret)
# 'https://61.160.247.63:808'
# 'https://60.191.201.38:45461'
# 'https://113.108.242.36:47713'
# 'https://27.17.45.90:43411'
# 'https://219.234.5.128:3128'
# 'https://101.64.32.100:808'
# 'https://101.236.59.11:8866'
import requests

if __name__ == '__main__':
    proxylist = [
                 'https://58.210.133.98:32741',
                 'https://58.240.7.195:32617',
                 'https://113.12.202.50:40498',
                 'https://114.119.116.92:61066',
                 'https://175.148.78.132:1133',
                 'https://121.31.177.90:8123']
    for proxy in proxylist:
        try:
            requests.get('https://sifa.sina.cn/2018-08-28/detail-ihiixyeu0494954.d.html?from=wap',
                         proxies={'https':proxy})
        except Exception as e:
            print('connect failed, url = %s' % proxy)
            print("exception: %s" % e)
        else:
            print('success, url = %s' % proxy)