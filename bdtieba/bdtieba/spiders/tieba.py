import json
import random
import re
import scrapy
from urllib.parse import quote

from ..settings import search_keywords
from ..items import BdtiebaItem
from .utils import check_releaseTime


class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    custom_settings = {
        'ITEM_PIPELINES': {'bdtieba.pipelines.BdtiebaPipeline': 300},
    }

    def start_requests(self):
        for keyword in search_keywords:
            # URL中文编码
            format_kw = quote(keyword, encoding='gb2312')
            url = f'https://tieba.baidu.com/f/search/res?isnew=1&kw=&qw={format_kw}&un=&rn=20&sd=&ed=&sm=1&only_thread=1&pn=1'
            yield scrapy.Request(url, callback=self.parse_postList, meta={'keyword': keyword})

    def parse_postList(self, response):
        """解析帖子列表"""

        # 是否请求下一页
        nextFlag = True

        # 解析当前页面数据
        post_items = response.xpath('//div[@class="s_post_list"]/div[@class="s_post"]')
        for item in post_items:
            title = item.xpath('./span[@class="p_title"]/a//text()').getall()  # 帖子标题
            post_id = item.xpath('./span[@class="p_title"]/a/@data-tid').get()  # 帖子ID

            post_name = item.xpath('./a[@class="p_forum"]/font//text()').get()  # 贴吧名
            author = item.xpath('./a[last()]/font/text()').get()  # 帖子作者
            releaseTime = item.xpath('./font[@class="p_green p_date"]/text()').get()  # 发布时间

            # 检查帖子发布时间
            time_status = check_releaseTime(releaseTime)
            if time_status == 1:
                # 可用
                postInfo = {
                    'keyword': response.meta['keyword'],
                    'title': "".join(title),
                    'post_id': post_id,
                    'post_name': post_name,
                    'author': author,
                    'releaseTime': releaseTime
                }
                # 请求每一个帖子
                yield scrapy.Request(f'https://tieba.baidu.com/mo?kz={post_id}', callback=self.parse_postContent,
                                     meta={'postInfo': postInfo})
            elif time_status == 0:
                # 跳过本次
                continue
            else:
                # 不再向下请求
                nextFlag = False
                break

        # 判断是否还有下一页
        next_pageUrl = response.xpath('//a[@class="next"]/@href').get()
        if next_pageUrl and nextFlag:
            # 补全 URL, 继续请求下一页
            full_url = response.urljoin(next_pageUrl)
            yield scrapy.Request(full_url, callback=self.parse_postList, meta={'keyword': response.meta['keyword']})

    def parse_postContent(self, response):
        """解析帖子内容"""

        postInfo = response.meta['postInfo']

        # 获取回帖数量
        title = response.xpath('//div[@class="bc p"]//text()').getall()
        post_comments = re.search(r'共(\d+)贴', "".join(title)).group(1)

        # 获取帖子内容
        post_content = response.xpath('//div[@class="d"]/div[1]/text()').getall()
        post_content = "".join(post_content).split('楼. ', maxsplit=1)[1]

        # 获取帖子回复
        replys = []  # 存储所有回复数据
        reply_lst = response.xpath('//div[@class="d"]/div[position()>1]')
        for item in reply_lst:
            reply_content = item.xpath('./text()').getall()
            reply_author = item.xpath('./table//span[@class="g"]/a/text()').get()
            reply_commentNum = item.xpath('./table//a[@class="reply_to"]/text()').get()

            # 正则匹配评论数量
            try:
                commentNum = re.search(r'回复\((\d+)\)', reply_commentNum).group(1)
            except AttributeError:
                commentNum = 0

            replys.append({
                'reply_content': "".join(reply_content).split('楼. ', maxsplit=1)[1],
                'reply_author': reply_author,
                'commentNum': int(commentNum)
            })

        # 获取最多人回复的评论
        if len(reply_lst) > 0:
            high_reply = max(replys, key=lambda x: x['commentNum'])
        else:
            high_reply = {"reply_content": None, "reply_author": None, "commentNum": None}

        postInfo.update(high_reply)
        postInfo.update({
            'post_content': post_content,
            'post_comments': post_comments,
        })

        tiebaItem = BdtiebaItem()
        tiebaItem['keyword'] = postInfo['keyword']
        tiebaItem['post_id'] = postInfo['post_id']
        tiebaItem['post_name'] = postInfo['post_name']
        tiebaItem['post_author'] = postInfo['author']
        tiebaItem['post_title'] = postInfo['title']
        tiebaItem['post_content'] = postInfo['post_content']
        tiebaItem['release_time'] = postInfo['releaseTime']
        tiebaItem['post_comments'] = postInfo['post_comments']
        tiebaItem['reply_content'] = postInfo['reply_content']
        tiebaItem['reply_author'] = postInfo['reply_author']
        tiebaItem['reply_comments'] = postInfo['commentNum']
        yield tiebaItem
