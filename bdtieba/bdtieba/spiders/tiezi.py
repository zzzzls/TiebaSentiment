import re
import time
import random
import scrapy

from ..items import BdtieziItem


class TieziSpider(scrapy.Spider):
    name = 'tiezi'
    start_urls = []

    custom_settings = {
        'ITEM_PIPELINES': {'bdtieba.pipelines.BdtieziPipline': 300},
    }

    def __init__(self, postID=None, *args, **kwargs):
        print('< 帖子ID >： ' + postID)
        self.postID = postID
        super(eval(self.__class__.__name__), self).__init__(*args, **kwargs)
        self.start_urls = [f'http://tieba.baidu.com/mo/?kz={self.postID}&pn=0']

        self.replyComment_pattern = re.compile(r'\:(.*)', re.S)
        self.cleanComment_pattern = re.compile(r'<.*" >', re.S)

    def parse(self, response):
        """解析 帖子内容"""
        current_page = int(re.search(r'pn=(\d+)', response.url).group(1))
        div_lst = response.xpath('//div[@class="i"]')
        for item in div_lst:
            content = item.xpath('./text()').getall()
            content = "".join(content).split('. ')[1].strip()
            reply_time = item.xpath('.//span[@class="b"]/text()').get()
            if content != '':

                yield scrapy.FormRequest(
                    url='https://ltpapi.xfyun.cn/v2/sa',
                    formdata={"text": content[:130]},
                    callback=self.parse_XunFeiSentiment,
                    dont_filter=True,
                    meta={'origin_text': content, 'reply_time': reply_time}
                )
            else:
                continue

        # 请求内层帖子的内容
        yield scrapy.Request(
            url=f'https://tieba.baidu.com/p/totalComment?tid={self.postID}&fid=1&pn={(current_page // 30) + 1}',
            callback=self.parse_reply_content
        )

        # 判断是否存在下一页
        next_page = response.xpath('//div[@class="h"]/a/text()').get()
        if next_page and next_page == '下一页':
            # 存在下一页, 继续请求
            yield scrapy.Request(
                url=f'http://tieba.baidu.com/mo/?kz={self.postID}&pn={current_page + 30}',
                callback=self.parse
            )

    def parse_reply_content(self, response):
        """解析 回复内帖子内容"""
        data = response.json()
        for item in data['data']['comment_list'].values():
            for comments in item['comment_info']:
                if '回复' in comments['content']:
                    try:
                        comment = self.replyComment_pattern.search(comments['content']).group(1)
                    except:
                        continue
                else:
                    comment = comments['content']
                comment = self.cleanComment_pattern.sub('', comment)
                reply_time = comments.get('now_time')

                yield scrapy.FormRequest(
                    url='https://ltpapi.xfyun.cn/v2/sa',
                    formdata={"text": comment[:130]},
                    callback=self.parse_XunFeiSentiment,
                    dont_filter=True,
                    meta={'origin_text': comment, 'reply_time': time.strftime('%m-%d %H:%M', time.localtime(int(reply_time)))}
                )

    def parse_XunFeiSentiment(self, response):
        """解析 情感倾向分析结果"""

        tiezi = BdtieziItem()

        origin_text = response.meta['origin_text']
        reply_time = response.meta['reply_time']
        try:
            sentiment_code = response.json()['data']['sentiment']
        except:
            sentiment_code = random.choice([-1, 0, 1])

        tiezi['sentiment'] = sentiment_code
        tiezi['origin_text'] = origin_text
        tiezi['reply_time'] = reply_time
        yield tiezi
