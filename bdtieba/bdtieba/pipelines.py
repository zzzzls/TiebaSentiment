# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pymysql
from datetime import date

from scrapy.exceptions import DropItem

from .settings import MySQLConfig, filter_postName


class BdtiebaPipeline:
    def open_spider(self, spider):
        # 连接 mysql 数据库
        self.conn = pymysql.connect(
            host=MySQLConfig['host'],
            user=MySQLConfig['user'],
            password=MySQLConfig['passwd'],
            database=MySQLConfig['db'],
            charset='utf8mb4',
            port=3308
        )
        self.cur = self.conn.cursor()
        self.cur.execute('truncate table tieba')  # 清空表

    def process_item(self, item, spider):
        for postName in filter_postName:
            # 通过贴吧名过滤数据
            if postName in item['post_name']:
                raise DropItem(f"开始过滤 {item['post_name']} 贴吧数据...")
        else:
            sql = "INSERT INTO tieba(keyword,post_id,post_name,post_author,post_title,post_content,release_time,post_comments,reply_content,reply_author,reply_comments) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(sql, list(item.values()))
            self.conn.commit()
            return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()


class BdtieziPipline:
    def __init__(self):
        # 连接 mysql 数据库
        self.conn = pymysql.connect(
            host=MySQLConfig['host'],
            user=MySQLConfig['user'],
            password=MySQLConfig['passwd'],
            database=MySQLConfig['db'],
            charset='utf8mb4',
            port=3308
        )
        self.cur = self.conn.cursor()
        self.cur.execute('truncate table tiezi')  # 清空表

    def process_item(self, item, spider):
        # 格式化时间
        if '-' not in item['reply_time']:
            item['reply_time'] = date.today().strftime('%Y-%m-%d') + ' ' + item['reply_time']
        else:
            item['reply_time'] = '2021-' + item['reply_time']
        sql = "INSERT INTO tiezi(comment, releaseTime, sentiment) VALUES(%s, %s, %s)"
        self.cur.execute(sql, [item['origin_text'], item['reply_time'], item['sentiment']])
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
