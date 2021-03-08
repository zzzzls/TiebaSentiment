## 项目简介

**基于百度贴吧帖子评论的舆情分析系统**，全站检索包含指定关键词的帖子，对帖子的回帖内容进行情感倾向分析及数据挖掘，可定时爬取数据，通过邮件发送生成的 word 舆情分析报告！



## 项目结构

![项目结构][项目结构]



## 环境依赖

```
python=3.7

Scrapy==2.4.1
numpy==1.20.1
pandas==1.2.3
matplotlib==3.3.4
PyMySQL==1.0.2
Pillow==8.1.2
docxtpl==0.11.3
jieba==0.42.1
wordcloud==1.8.1
```



## 目录结构描述

```
bdtieba
    │  1.start.py                负责启动爬虫，爬取数据
    │  2.send_mail.py            负责绘制图表，生成word，发送邮件
    │  scrapy.cfg
    │  回帖量数据图.png            生成的资源数据
    │  热点舆情报告.docx
    │  词云.png
    │  近三日舆情报告.docx
    │
    ├─bdtieba
    │  │  items.py               定义爬虫需要爬取的字段
    │  │  middlewares.py         爬虫中间件，配置 讯代理 及 讯飞情感分析接口
    │  │  pipelines.py           管道文件，负责存储爬取的数据  内部实现帖子过滤
    │  │  settings.py            爬虫配置文件，定义 Mysql配置，讯代理\讯飞接口 账号密码等
    │  │  __init__.py
    │  │
    │  ├─spiders
    │  │  │  tieba.py            负责爬取贴吧数据
    │  │  │  tiezi.py            负责爬取帖子详情数据
    │  │  │  utils.py            定义功能函数，如 md5加密 及 发帖时间检测
    │  │  │  __init__.py
    │  │  │
    └─static
            mb_热点舆情报告.docx     word报告模板
            mb_近三日舆情报告.docx
            方正卡通简体.ttf         词云所用字体
```




## 部署步骤

1. 通过 sql 文件创建 Mysql 数据库，数据表
2.  `settings.py` 中配置 `讯代理`，`讯飞开放平台`，`mysql`
3. `send_mail.py` 中配置 `邮箱smtp服务`，`mysql`

4. 修改 `scrapy` 源码

   ```
   scrapy源代码中查找http11.py文件，相对路径为：
   
   Lib/site-packages/scrapy/core/downloader/handlers/http11.py
   
   找到下面内容，注释掉：
   
   if isinstance(agent, self._TunnelingAgent):
      headers.removeHeader(b’Proxy-Authorization’)
      
   否则 proxy-authorization 会被去除，讯代理动态转发失效
   ```

5. 启动 `1.start.py` 启动爬虫，爬取数据

6. 启动 `2.send_mail.py ` 生成报告，发送邮件






[项目结构]: ./项目结构.png

