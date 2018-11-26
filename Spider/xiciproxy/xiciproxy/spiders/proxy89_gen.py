# coding=utf-8
# IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
# 仅仅爬取首页IP地址就足够一般使用

#精通scrapy网络爬虫（2017）,终端运行scrapy crawl xici_proxy -o proxy_list.json，生成可用的免费代理列表
import scrapy
from scrapy.http import Request
import json
class XiciSpider(scrapy.Spider):
    name = "proxy89"
    allowed_domains = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    def start_requests(self):
        #爬取http://www.xicidaili.com/nn/前3页
        for i in range(1, 10):
            yield Request('http://www.89ip.cn/index_%s.html' % i, callback=self.parse, headers=self.headers)

    def parse(self, response):
        for sel in response.xpath('//tbody//tr'):#//*[@id="proxies_table"]/tbody/tr[1]/td[1]/text()
            # 提取代理的IP、port、scheme(http or https)
            ip_port = sel.css('td:nth-child(1)::text').extract()
            ip,port = ip_port.split(':')
            scheme = 'http'
            # 使用爬取到的代理再次发送请求到http(s)://httpbin.org/ip，验证代理是否可用
            url = '%s://httpbin.org/ip' % scheme
            proxy = '%s://%s:%s' % (scheme, ip, port)
            meta = {
                'proxy': proxy,
                'dont_retry': True,
                'download_timeout': 10,
               # 以下两个字段是传递给check_available 方法的信息，方便检测
                '_proxy_scheme': scheme,
                '_proxy_ip': ip,
            }
            yield Request(url, callback=self.check_available,
                          meta=meta, dont_filter=True, headers=self.headers)
    def check_available(self, response):
        proxy_ip = response.meta['_proxy_ip']
        # 判断代理是否具有隐藏IP 功能
        if proxy_ip == json.loads(response.text)['origin']:
            yield {
                'proxy_scheme': response.meta['_proxy_scheme'],
                'proxy': response.meta['proxy'],
            }