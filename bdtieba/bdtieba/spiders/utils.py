import hashlib
from datetime import date, datetime, timedelta

def check_releaseTime(releaseTime, days_interval=3):
    """
    检查帖子发布时间是否在指定日期内
    默认间隔3天, 即 3天内(包含3天) 的帖子是可用的

    :param releaseTime:  帖子发布时间
    :param days_interval:  天数间隔
    :return:
        0 -- 时间格式错误
        1 -- 帖子发布时间合法
        -1 -- 帖子发布时间非法
    """
    # 获取当前日期
    try:
        current_date = date.today()
        target_date = datetime.strptime(releaseTime, '%Y-%m-%d %H:%M').date()
    except:
        return 0

    if (current_date - target_date) < timedelta(days=days_interval):
        return 1
    else:
        return -1


def md5Encrypy(obj):
    """
    md5加密
    """
    md5 = hashlib.md5()
    md5.update(obj.encode())
    return md5.hexdigest()






