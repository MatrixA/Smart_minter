import asyncio
import threading
import time
from datetime import timedelta,datetime
from ssl import SSLError
from time import sleep

from exception_process import *

import requests
import json
import random
import schedule as schedule

import conf as Config
from log import get_logger,clear_logs

PAGE_SIZE = Config.FETCH_MESSAGE_PAGE_SIZE
AUTH_TOKEN = Config.USER_DISCORD_TOKEN
CHANEL_LIST = Config.CHANEL_LIST
HOURS = Config.FETCH_MESSAGE_TIME_DELTA
logfile = "logs/discord_log.txt"
logger = get_logger(logfile)
# 保存最新信息时间
CHANEL_TIME_STAMP_DICT = {}


def tcp_echo_client(message):
    print("send message")
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    }
    params = {
        "msg": json.dumps(message)
    }
    print(params)
    response = requests.post("http://127.0.0.1:8082/discord_updated",headers=headers,params=params)
    print(response)

def wx_company_bot_echo_client(message):
    wx_company_bot.send_msg_list(message)

class Discord_Tool:
    def __init__(self,update_message = None):
        self.update_message = update_message

    def fetch_page_message(self,chanel_id, offset):
        headr = {
            "Authorization": AUTH_TOKEN,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
        }
        # chanel_id = random.choice(chanel_list)
        url = "https://discord.com/api/v9/channels/{}/messages?limit={}&offset={}".format(chanel_id, PAGE_SIZE, offset)
        print(url)
        print(headr)
        res = requests.get(url=url, headers=headr)
        res.encoding = "UTF-8"
        # print(res.text)
        result = json.loads(res.content)
        print(result)
        # exit()
        return result

    def fetch_more_message(self,chanel_id,lastest_begin_time_stamp):
        fetch_more = True
        message_list = []
        offset = 0
        while fetch_more:
            result = self.fetch_page_message(chanel_id, offset)
            if len(result) > 0:
                origin_date_str = result[0]['timestamp']
                first_item_stamp = datetime.strptime(origin_date_str, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
                # first_item_stamp = result[0]['timestamp']
                end_date_str = result[len(result) - 1]['timestamp']
                end_item_stamp = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
                if (lastest_begin_time_stamp is not None) and first_item_stamp < lastest_begin_time_stamp:
                    # 如果获取的聊天记录最近的时间戳早于当前已获取时间戳时间，则已获取过该信息
                    fetch_more = False
                    break
                elif (lastest_begin_time_stamp is not None) and end_item_stamp > lastest_begin_time_stamp:
                    # 如果获取的聊天记录最早的时间(离现在越远时间)大于当前已获取聊天记录时间戳，则为该次记录全未获取过，请求下一分页记录
                    message_list.extend(result)
                    self.process(result)
                    offset += PAGE_SIZE
                    fetch_more = True
                else:
                    # 交叉情况
                    fetch_more = False
                    for item in result:
                        item_str = item['timestamp']
                        item_stamp = datetime.strptime(item_str, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
                        if (lastest_begin_time_stamp is not None) and item_stamp > lastest_begin_time_stamp:
                            # 新消息
                            message_list.append(item)
                            self.process([item])
                        else:
                            # 已处理过的消息
                            break
            sleep(random.randrange(1, 5))
        # message、time_stamp
        print(message_list)
        return message_list

    def process(self,message_list):
        # process
        if Config.TELEGRAM_NOTIFY_ON:
            thread_telegram = threading.Thread(target=tcp_echo_client(message_list))
            thread_telegram.start()
        if Config.WX_COMPANY_NOTIFY_ON:
            thread_wx = threading.Thread(target=wx_company_bot_echo_client(message_list))
            thread_wx.start()
            
        # asyncio.run(tcp_echo_client(message_list))
        # asyncio.run(wx_echo_client(message_list))
        # self.update_message(message_list)

    def task_fetch(self):
        print(CHANEL_TIME_STAMP_DICT)
        for chanel_id in CHANEL_LIST:
            lastest_begin_time_stamp = CHANEL_TIME_STAMP_DICT[chanel_id]
            message_list = self.fetch_more_message(chanel_id,lastest_begin_time_stamp)
            if len(message_list) > 0:
                print("sssss")
                time_str = message_list[0]["timestamp"]
                time_stamp = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
                CHANEL_TIME_STAMP_DICT[chanel_id] = time_stamp
        print(CHANEL_TIME_STAMP_DICT)

    def execute_multi_task(self):
        time = datetime.now() - timedelta(hours=HOURS)
        for channel_id in CHANEL_LIST:
            CHANEL_TIME_STAMP_DICT[channel_id] = time.timestamp()
        # warning
        # debug模式立马fetch数据
        if Config.DEBUG:
            self.task_fetch()
        schedule.every(Config.FETCH_TASK_TIME_INTERVEL).minutes.do(self.task_fetch)  # 每隔 1 分钟运行一次 task_fetch 函数
        schedule.every(4).hours.do(clear_logs) #清理日志
        while True:
            schedule.run_pending()  # 运行所有可以运行的任务
            sleep(1)

if __name__ == "__main__":
    exception = None
    for _ in range(Config.MAX_TRY_AMOUNT):
        try:
            tool = Discord_Tool()
            tool.execute_multi_task()
        except SSLError as e:
            print(e)
            exception = e
            logger.exception(e)
            Config.MAX_TRY_AMOUNT += 1
            time.sleep(Config.TRY_TIME_TO_SLEEP)
        except Exception as e:
            print(e)
            exception = e
            logger.exception(e)
            time.sleep(Config.TRY_TIME_TO_SLEEP)

    send_wx_exception_msg(exception)