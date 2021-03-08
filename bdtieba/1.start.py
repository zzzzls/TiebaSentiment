import pymysql

from bdtieba.spiders.tieba import TiebaSpider
from bdtieba.spiders.tiezi import TieziSpider
from bdtieba.settings import MySQLConfig

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from twisted.internet import reactor, defer

configure_logging()
runner = CrawlerRunner()


def query_max_comments():
    # 查询回复量最高帖子
    conn = pymysql.connect(
        host=MySQLConfig['host'],
        user=MySQLConfig['user'],
        password=MySQLConfig['passwd'],
        database=MySQLConfig['db'],
        port=3308,
        charset='utf8mb4',
    )
    cur = conn.cursor()
    sql = 'select post_id from tieba where post_comments = (select max(post_comments) from tieba)'
    cur.execute(sql)
    post_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return post_id


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(TiebaSpider)
    print('开始执行第二个')
    post_id = query_max_comments()
    yield runner.crawl(TieziSpider, postID=post_id)
    print('执行结束')
    reactor.stop()


crawl()
reactor.run()
