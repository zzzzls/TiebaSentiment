# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import time
import hashlib
from scrapy import signals

from .spiders.utils import md5Encrypy
from .settings import XunFeiAI, XunDaiLi

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class BdtiebaSpiderMiddleware:
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

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
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


class BdtiebaDownloaderMiddleware:
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
        if request.url.startswith('https://ltpapi.xfyun.cn'):
            curTime = str(int(time.time()))

            request.headers.update({
                'X-Appid': XunFeiAI['appid'],
                'X-CurTime': curTime,
                'X-Param': XunFeiAI['x_param'],
                'X-CheckSum': md5Encrypy(XunFeiAI['appkey'] + curTime + XunFeiAI['x_param']),
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            })
            request.headers.pop('Host')
        else:
            # 讯代理
            orderno = XunDaiLi['order']  # 订单号
            secret = XunDaiLi['secret']  # 密钥
            request.meta['proxy'] = 'http://forward.xdaili.cn:80'
            timestamp = str(int(time.time()))  # timestamp
            string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
            md5_string = hashlib.md5(string.encode('utf-8')).hexdigest()  # sign
            sign = md5_string.upper()
            auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
            request.headers["Proxy-Authorization"] = auth
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
