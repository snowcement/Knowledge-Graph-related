# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import logging
import time
from collections import defaultdict
from scrapy.exceptions import NotConfigured
import json
from faker import Faker
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, TCPTimedOutError, ConnectionRefusedError, ConnectionDone, ConnectError, ConnectionLost
from twisted.web._newclient import ResponseNeverReceived
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http import HtmlResponse
from scrapy.utils.response import response_status_message
import copy

logger = logging.getLogger(__name__)
PROXY_LIST = defaultdict(list)

class SinasfnewsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SinasfnewsDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError, ResponseNeverReceived)
    def process_response(self,request,response,spider):
        #捕获状态码为40x/50x的response
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            #随意封装，直接返回response，spider代码中根据url==''来处理response
            response = HtmlResponse(url='')
            return response
        #其他状态码不处理
        return response
    def process_exception(self,request,exception,spider):
        #捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            #在日志中打印异常类型
            print('Got exception: %s' % (exception))
            #随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response
        #打印出未捕获到的异常
        print('not contained exception: %s'%exception)


class RandomHttpProxyMiddleware(HttpProxyMiddleware):
    def __init__(self, auth_encoding='latin-1', proxy_list_file=None):
        super(RandomHttpProxyMiddleware, self).__init__()
        if not proxy_list_file:
            raise NotConfigured

        self.auth_encoding = auth_encoding
        # 分别用两个列表维护HTTP和HTTPS的代理，{'http': [...], 'https': [...]}
        self.proxies = defaultdict(list)
        # 从json文件中读取代理服务器信息，填入self.proxies
        with open(proxy_list_file) as f:
            proxy_list = json.load(f)
            for proxy in proxy_list:
                scheme = proxy['proxy_scheme']
                url = proxy['proxy']
                self.proxies[scheme].append(self._get_proxy(url, scheme))
        global PROXY_LIST
        PROXY_LIST = copy.deepcopy(self.proxies)
    @classmethod
    def from_crawler(cls, crawler):
        # 从配置文件中读取用户验证信息的编码
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING', 'latin-1')
        # 从配置文件中读取代理服务器列表文件（json）的路径
        proxy_list_file = crawler.settings.get('HTTPPROXY_PROXY_LIST_FILE')
        return cls(auth_encoding, proxy_list_file)

    def _set_proxy(self, request, scheme):
        # 随机选择一个代理
        creds, proxy = random.choice(self.proxies[scheme])
        request.meta['proxy'] = proxy
        #当横向爬取page=**的其他页面，去掉headers中的Referer字段，去掉meta中的depth字段，防止频繁返回403 Forbidden
        #纵向爬取**.shtml时，request无需删除字段
        ret = request.url.find('&page=')
        if ret != -1:
            dep = request.meta.get('depth', None)
            if dep:
                request.meta.pop('depth')
            ref = request.headers.get('Referer', None)
            if ref:
                request.headers.pop('Referer')
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic ' + creds

class RandomUserAgentMiddleware(object):

    def __init__(self):
        self.faker = Faker(local='zh_CN')
        self.user_agent = ''

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, 'user_agent',self.user_agent)

    def process_request(self, request, spider):
        self.user_agent = self.faker.user_agent()       #获得随机user_agent
        request.headers.setdefault(b'User-Agent', self.user_agent)

#https://www.jianshu.com/p/f520ba05d2dc scrapy下载中间件

class MyRetryMiddleware(RetryMiddleware):
    logger = logging.getLogger(__name__)

    def delete_proxy(self, proxy):
        if proxy:
            # delete proxy from proxies pool
            logging.error("Invalid proxy: %s" % proxy)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            self.delete_proxy(request.meta.get('proxy', False))
            time.sleep(random.randint(3, 5))
            self.logger.warning('返回值异常, 进行重试...')
            return self.retry(request, reason, spider) or response
        return response


    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            # 删除该代理
            self.delete_proxy(request.meta.get('proxy', False))
            time.sleep(random.randint(3, 5))
            self.logger.warning('连接异常, 进行重试...')

            return self.retry(request, exception, spider)

    def retry(self, request, reason, spider):
        #更换request中的代理IP
        proxy = request.meta['proxy']
        index = proxy.index(':')
        scheme = proxy[:index]
        creds, proxynew = random.choice(PROXY_LIST[scheme])
        request.meta['proxy'] = proxynew
        return self._retry(request, reason, spider)

#原文：https://blog.csdn.net/qq_33854211/article/details/78535963