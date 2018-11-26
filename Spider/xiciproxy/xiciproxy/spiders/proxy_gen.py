# coding=utf-8
# IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
# 仅仅爬取首页IP地址就足够一般使用

#http://blog.51cto.com/7200087/2070320
# from bs4 import BeautifulSoup
# import requests
# import random
#
# def get_ip_list(url, headers):
#     web_data = requests.get(url, headers=headers)
#     soup = BeautifulSoup(web_data.text, 'lxml')
#     ips = soup.find_all('tr')
#     ip_list = []
#     for i in range(1, len(ips)):
#         ip_info = ips[i]
#         tds = ip_info.find_all('td')
#         ip_list.append(tds[1].text + ':' + tds[2].text)
#     return ip_list
#
# def get_random_ip(ip_list):
#     proxy_list = []
#     for ip in ip_list:
#         proxy_list.append('http://' + ip)
#     proxy_ip = random.choice(proxy_list)
#     proxies = {'http': proxy_ip}
#     return proxies, proxy_list

#精通scrapy网络爬虫（2017）,终端运行scrapy crawl xici_proxy -o proxy_list.json，生成可用的免费代理列表
import scrapy
from scrapy.http import Request
import json
class XiciSpider(scrapy.Spider):
    name = "xici"
    allowed_domains = ["www.xicidaili.com"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    def start_requests(self):
        #爬取http://www.xicidaili.com/nn/前3页
        for i in range(1, 4):
            yield Request('http://www.xicidaili.com/nn/%s' % i, callback=self.parse, headers=self.headers)
    def parse(self, response):
        for sel in response.xpath('//table[@id="ip_list"]/tr[position()>1]'):
            # 提取代理的IP、port、scheme(http or https)
            ip = sel.css('td:nth-child(2)::text').extract_first()
            port  = sel.css('td:nth-child(3)::text').extract_first()
            scheme = sel.css('td:nth-child(6)::text').extract_first().lower()
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


# if __name__ == '__main__':
#     url = 'http://www.xicidaili.com/nn/'
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
#     }
#     ip_list = get_ip_list(url, headers=headers)
#     proxies, proxieslist = get_random_ip(ip_list)
#     print(proxies)
#     print(proxieslist)