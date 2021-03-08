import pymysql
import jieba.analyse
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from wordcloud import WordCloud
from docxtpl import DocxTemplate

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置连接 Mysql
MySQLConfig = {
    'host': '**',
    'db': '**',
    'user': '**',
    'port': 3308,
    'passwd': '**'
}
# 配置词云字体路径
WordCloud_font_path = r'./static/方正卡通简体.ttf'

# 邮件配置
user = '**'  # 发送者邮箱
pwd = '**'  # 授权码
to = '**'  # 接受人

# 从数据库中读取数据
conn = pymysql.connect(
    user=MySQLConfig['user'],
    password=MySQLConfig['passwd'],
    host=MySQLConfig['host'],
    database=MySQLConfig['db'],
    charset='utf8mb4',
    port=3308
)
post_df = pd.read_sql_query('SELECT * FROM tieba', conn)  # 帖子数据
comments_df = pd.read_sql_query('SELECT * FROM tiezi', conn)  # 评论数据

# 筛选回复量前10的帖子
top_post = post_df.sort_values(by='post_comments', ascending=False).head(10)
top_post['post_id'] = top_post['post_id'].transform(lambda x: 'https://tieba.baidu.com/p/' + str(x))
post_lsts = top_post.loc[:, ['post_id', 'post_author', 'post_title', 'release_time', 'post_comments']].values


def draw_wordcloud(comments):
    """绘制词云"""
    cloud = WordCloud(
        scale=3,
        # 设置字体
        font_path=WordCloud_font_path,
        # 设置背景色
        background_color='white',
        # 允许最大词汇
        max_words=1000,
        # 最大号字体
        max_font_size=50
    )

    wCloud = cloud.generate(" ".join(comments))
    wCloud.to_file('./词云.png')


# 使用 jieba 提取帖子回复中关键字
comments_kw = []
for comment in comments_df['comment'].tolist():
    comments_kw.extend(jieba.analyse.extract_tags(comment, topK=13))

draw_wordcloud(comments_kw)  # 绘制词云图

# 分组统计评论情感倾向数量
sentiment_lst = comments_df.groupby('sentiment')['sentiment'].count()

comments_df['releaseTime'] = pd.to_datetime(comments_df['releaseTime'])
# 根据评论时间对数据进行离散化
cut_result = pd.cut(comments_df['releaseTime'], 6, right=False, retbins=True)
releaseTime = cut_result[0]
date_group = cut_result[1]

reply_count = releaseTime.value_counts().reset_index().sort_values('index')['releaseTime'].tolist()
reply_count.insert(0, 1)

date_group = [item.strftime('%m-%d %H:%M') for item in date_group.tolist()]

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.subplots_adjust(bottom=3, top=4, left=0, right=1, wspace=0.8)

fig = plt.figure(figsize=(16, 7.5), dpi=100)

# 绘制饼图
img1 = fig.add_subplot(1, 2, 2)
labels = ['贬义', '中性', '褒义']
img1.pie(sentiment_lst.tolist(), labels=labels, autopct='%1.1f%%', shadow=False, startangle=150,
         colors=['#2ca02c', '#1f77b4', '#ff7f0e'])
plt.axis('equal')
plt.title("回帖情感倾向分析")
plt.legend(loc="upper right", fontsize=10, bbox_to_anchor=(1.1, 1.05), borderaxespad=0.3, labels=labels)

# 绘制折线图
img2 = fig.add_subplot(1, 2, 1)
x = [i for i in range(1, len(date_group) + 1)]
img2.plot(x, reply_count, "#ee863f", marker='.', ms=8, label="a")
plt.xticks(rotation=45)
plt.xlabel("时间段")
plt.ylabel("回帖量")
plt.title("回帖量随时间段变化折线图")
# 在折线图上显示具体数值, ha参数控制水平对齐方式, va控制垂直对齐方式
for x1, y1 in zip(x, reply_count):
    plt.text(x1, y1 + 0.3, str(y1), ha='center', va='bottom', fontsize=15, rotation=0)
plt.xticks(x, date_group)
plt.savefig("./回帖量数据图.png")

# 生成近三日舆情报告 word 文档
doc = DocxTemplate(r"./static/mb_近三日舆情报告.docx")
current_date = date.today()
last_date = current_date - timedelta(days=2)
dct = {"post_lsts": post_lsts, 'current_date': current_date, 'last_date': last_date}
doc.render(dct)
doc.save(r"./近三日舆情报告.docx")

# 生成 热点舆情报告 word文档
postData = top_post.iloc[0]

doc = DocxTemplate(r"./static/mb_热点舆情报告.docx")
dct = {
    "post_title": postData['post_title'],
    'date': postData['release_time'].split(' ')[0],
    'author': postData['post_author'],
    'releaseTime': postData['release_time'],
    'reply_comment': postData['post_comments'],
    'url': postData['post_id']
}
doc.replace_pic("Picture 8", '回帖量数据图.png')
doc.replace_pic("图片 1", '词云.png')
doc.render(dct)
doc.save(r"./热点舆情报告.docx")

# 发送邮件

# 1.设置一个可以添加正文和附件的msg
msg = MIMEMultipart()

# 2.先添加正文内容，设置HTML格式的邮件正文内容
mail_msg = "涉警网络舆情分析报告"
msg.attach(MIMEText(mail_msg, 'html', 'utf-8'))

# 3.再添加附件，这里的文件名可以有中文，但下面第三行的filename不可以为中文
att1 = MIMEText(open('./热点舆情报告.docx', 'rb').read(), 'base64', 'utf-8')
att1["Content-Type"] = 'application/octet-stream'
att1["Content-Disposition"] = 'attachment; filename="Hot_public_opinion.docx"'

att2 = MIMEText(open('./近三日舆情报告.docx', 'rb').read(), 'base64', 'utf-8')
att2["Content-Type"] = 'application/octet-stream'
att2["Content-Disposition"] = 'attachment; filename="Three_days_public_opinion.docx"'

msg.attach(att1)
msg.attach(att2)

# 4.设置邮件主题、发件人、收件人
msg['Subject'] = '涉警网络舆情分析报告'
msg['From'] = user
msg['To'] = to

# 5.发送邮件
s = smtplib.SMTP_SSL('smtp.qq.com', 465)
s.login(user, pwd)
s.send_message(msg)  # 发送邮件
s.quit()
print('Success!')
