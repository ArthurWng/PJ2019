# -*-coding:utf-8-*-

import itchat
from time import sleep,time
import random
import requests
import re
from datetime import datetime, timedelta
import time

import pymysql


conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='test', charset='utf8')
cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

seconds = float("0."+str(random.randrange(1, 10)))


def call_cqssc_api():
    api_url = 'http://f.apiplus.net/cqssc-20.json'
    try:
        r = requests.request('get', api_url)  # 访问接口
        return r.json()
    except Exception:  # 免费的，访问间隔不小于10秒
        return 'error'


def get_now_time():
    # 获取当前时间
    now_time = datetime.now()
    now_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
    now_time = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
    return now_time


def get_date_time(time_stamp):
    # 将时间戳转换成%Y-%m-%d %H:%M:%S格式
    date_time = datetime.fromtimestamp(time_stamp)
    return date_time


def get_date_time_str(time_str):
    # 将拼接的时间字符串转换成%Y-%m-%d %H:%M:%S格式
    date_time_str = get_time_stamp(time_str)
    wave_time = get_date_time(date_time_str)
    return wave_time


def get_time_stamp(time_str):
    # 将字符串格式时间转换成时间戳
    time_stamp = time.strptime(time_str,'%Y-%m-%d %H:%M:%S')
    time_stamp = int(time.mktime(time_stamp))  # 获取秒级时间戳
    return time_stamp


def get_api_params(response):
    # 获取号码
    get_code = response["data"][0]["opencode"]
    open_code = get_code.replace(",", " ")

    # 获取季数
    get_period_num = response["data"][0]["expect"]
    period_num_list = re.match(r'\d{8}(\d{3})',get_period_num)
    period_num = period_num_list.group(1)

    # 获取opentime
    open_time = response["data"][0]["opentimestamp"]

    return period_num, open_code, open_time


def get_border_time():
    # 第一段时间
    # 上午10:00:00
    ten_clock_am = time.strftime('%Y-%m-%d',time.localtime())+' 10:00:00'
    ten_clock_am = get_date_time_str(ten_clock_am)

    # 下午22:00:00
    ten_clock_pm = time.strftime('%Y-%m-%d',time.localtime())+' 23:00:00'
    ten_clock_pm = get_date_time_str(ten_clock_pm)
    # print(ten_clock_pm)

    # 第二段时间
    # 次日02:00:00
    two_clock = time.strftime('%Y-%m-%d',time.localtime(time.time()+86400))+' 02:00:00'
    two_clock = get_date_time_str(two_clock)
    # print(two_clock)

    return ten_clock_am, ten_clock_pm, two_clock


def auto_send_msg():
    # 群聊注册
    # get_chatrooms = input('请输入客户的群聊名称: ')

    # 登录微信
    itchat.auto_login(hotReload=True)

    # chat_rooms = itchat.search_chatrooms(name=get_chatrooms)
    chat_rooms = 'filehelper'

    # 获取当前开启时间
    api_response = call_cqssc_api()
    period_num, open_code, open_time = get_api_params(api_response)
    open_time = get_date_time(open_time)
    print('previous period code is %s' % open_code)

    # 获取下次开启时间，单位秒
    next_time = 500
    next_open_time = open_time + timedelta(seconds=next_time)  # 相隔10分钟
    print('next open time is %s' % next_open_time)

    # 获取当前时间
    now_time = get_now_time()

    # 获取时间边界
    ten_clock_am, ten_clock_pm, two_clock = get_border_time()

    while ten_clock_am <= now_time <= two_clock:

        now_time = get_now_time()
        if now_time <= ten_clock_pm:

            if now_time == ten_clock_am:
                itchat.send_msg('start.gif', chat_rooms)
                itchat.send_msg('第%d' % int(period_num) + " 季阳光指数：%s" % open_code, chat_rooms)

            elif now_time < next_open_time:
                if str(next_open_time-now_time) == '0:00:30':
                    cursor.execute("select shengjiang from data")
                    t = str(cursor.fetchall())
                    print(t)
                    itchat.send_msg(t, chat_rooms)

                    itchat.send_msg('第%d' % (int(period_num)+1) + '季：距离收割还剩30秒！[奋斗][奋斗]', chat_rooms)



                    sleep(1)
                else:
                    pass

            elif now_time == next_open_time:
                api_response = call_cqssc_api()
                period_num, open_code, open_time = get_api_params(api_response)
                next_open_time = next_open_time + timedelta(seconds=next_time)

                itchat.send_image('stop.gif', chat_rooms)
                sleep(1)
                itchat.send_msg('第%d' % int(period_num) + " 季阳光指数：%s" % open_code, chat_rooms)
                sleep(2)
                itchat.send_image('start.gif', chat_rooms)
                sleep(1)
                itchat.send_msg("第%d" % (int(period_num)+1)+ " 季活动开始", chat_rooms)
                # print("Now is No.%d" % (int(period_num)+1))
                sleep(1)  # 避免同一毫秒，代码被多次执行
                print('previous period code is %s' % open_code)
                print('next open time is %s' % next_open_time)
        else:
            if now_time == ten_clock_am:
                itchat.send_msg('第%d' % int(period_num) + " 季阳光指数：%s" % open_code, chat_rooms)
                itchat.send_image('start.gif', chat_rooms)

            elif now_time < next_open_time:
                if str(next_open_time-now_time) == '0:00:30':
                    itchat.send_msg('第%d' % int(period_num) + '季：距离收割还剩30秒！[奋斗][奋斗]', chat_rooms)
                    sleep(1)
                else:
                    pass

            elif now_time == next_open_time:
                api_response = call_cqssc_api()
                period_num, open_code, open_time = get_api_params(api_response)
                next_open_time = next_open_time + timedelta(seconds=next_time-300)

                itchat.send_image('stop.gif', chat_rooms)
                itchat.send_msg('第%d' % int(period_num) + " 季阳光指数：%s" % open_code, chat_rooms)
                itchat.send_image('start.gif', chat_rooms)
                itchat.send_msg("第%d" % (int(period_num)+1)+ " 季活动开始", chat_rooms)
                # print("Now is No.%d" % (int(period_num)+1))
                sleep(1)  # 避免同一毫秒，代码被多次执行


if __name__ == '__main__':
    auto_send_msg()
