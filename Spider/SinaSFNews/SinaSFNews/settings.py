# -*- coding: utf-8 -*-

# Scrapy settings for SinaSFNews project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'SinaSFNews'

SPIDER_MODULES = ['SinaSFNews.spiders']
NEWSPIDER_MODULE = 'SinaSFNews.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'SinaSFNews (+http://www.yourdomain.com)'
#USER_AGENT = 'User-Agent:Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0;'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.25
DOWNLOAD_TIMEOUT = 15#下载器在超时前等待的时间量（以秒为单位）
RANDOMIZE_DOWNLOAD_DELAY = True#在从同一网站获取请求时等待随机时间,降低了由分析请求的站点检测（并随后阻塞）爬行器的机会

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'SinaSFNews.middlewares.SinasfnewsSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   #使用随机用户代理与IP代理
   'SinaSFNews.middlewares.MyRetryMiddleware': 130,
   'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
   #'SinaSFNews.middlewares.ProcessAllExceptionMiddleware': 120,
   'SinaSFNews.middlewares.RandomHttpProxyMiddleware': 543,
   'SinaSFNews.middlewares.RandomUserAgentMiddleware': 550,
   'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}
# 使用之前在http://www.xicidaili.com/网站爬取到的代理
HTTPPROXY_PROXY_LIST_FILE='/xxxx/SinaSFNews/proxy_list.json'#设置为你的路径

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
MYSQL_DB_NAME = 'xxx'#你的数据库名
MYSQL_HOST = 'xx.x.xx.xxx'#数据库所在主机IP
MYSQL_USER = 'xxx'#连接数据库的用户名
MYSQL_PASSWORD = 'xxx'#连接数据库的密码
ITEM_PIPELINES = {
   'SinaSFNews.pipelines.MySQLAsyncPipeline': 401,
   #'SinaSFNews.pipelines.SinasfnewsPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True #自动限速开启
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60 # 设置最大下载延时
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False #开启[自动限速]的debug

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

RETRY_ENABLED = True
RETRY_TIMES = 15
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 400, 403, 404, 408]
