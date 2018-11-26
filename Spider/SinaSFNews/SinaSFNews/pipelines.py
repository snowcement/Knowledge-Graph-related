# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import pymysql.cursors
import traceback
#利用twisted提供的异步方式多线程访问数据库模块adbapi,提高程序访问数据库的效率
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
import threading

#mysql -uxxx -pxxx -h'xx.x.xx.xxx'
class SinasfnewsPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLAsyncPipeline:
    def open_spider(self, spider):
        db = spider.settings.get('MYSQL_DB_NAME', 'xxx')#你的数据库名
        host = spider.settings.get('MYSQL_HOST', 'xx.x.xx.xxx')#数据库所在主机IP
        port = spider.settings.get('MYSQL_PORT', 3306)
        user = spider.settings.get('MYSQL_USER', 'xxx')#连接数据库的用户名
        passwd = spider.settings.get('MYSQL_PASSWORD', 'xxx')#连接数据库的密码
        # self.db_conn = pymysql.connect(host=host, port=port, db=db,
        #                                user=user, passwd=passwd, charset='utf8')
        self.dbpool = adbapi.ConnectionPool('pymysql', host=host, db=db, port=port,
                                            user=user, passwd=passwd,
                                            cursorclass=pymysql.cursors.DictCursor,
                                            connect_timeout=5,
                                            use_unicode=True,
                                            charset='utf8')# MySQLdb-----cursorclass=pymysql.cursors,

    def close_spider(self, spider):
        self.dbpool.close()

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        #以异步方式调用insert_db函数
        try:
            yield self.dbpool.runInteraction(self.insert_db, item)
        except:
            print(traceback.format_exc())

        defer.returnValue(item)
        # return item

    def insert_db(self, tx, item):
        values = (
            item.get('title',''),
            item.get('content',''),
            item.get('time',''),
            item.get('tag',''),
            item.get('origin',''),
            item.get('url',''),
        )
        if len(values[0])== 0:#values(tuple list)
            return
        sql = 'INSERT INTO scrapy_sinasfnews VALUES (%s,%s,%s,%s,%s,%s)'
        tx.execute(sql, values)