# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BdtiebaItem(scrapy.Item):
    # define the fields for your item here like:
    keyword = scrapy.Field()  # 搜索关键字
    post_id = scrapy.Field()  # 帖子ID
    post_name = scrapy.Field()  # 贴吧名
    post_author = scrapy.Field()  # 帖子作者
    post_title = scrapy.Field()  # 帖子标题
    post_content = scrapy.Field()  # 帖子内容
    release_time = scrapy.Field()  # 发布时间
    post_comments = scrapy.Field()  # 回帖人数
    reply_content = scrapy.Field()  # 回帖内容
    reply_author = scrapy.Field()  # 回帖作者
    reply_comments = scrapy.Field()  # 回帖评论数

class BdtieziItem(scrapy.Item):
    origin_text = scrapy.Field()  # 帖子文本
    reply_time = scrapy.Field()  # 回帖时间
    sentiment = scrapy.Field()  # 情感分析结果