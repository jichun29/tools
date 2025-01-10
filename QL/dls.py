'''
微信小程序：杜蕾斯会员中心
杜蕾斯 2.0.0
变量名 dls
抓 vip.ixiliu.cn 域名中 access-token
多账号使用&分割
定时每天1次即可
'''
import time
import requests
import os
from notify import send


def get_headers(token):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/8555",
        "content-type": "application/json;charset=utf-8",
        "sid": "10006",
        "xweb_xhr": "1",
        "platform": "MP-WEIXIN",
        "enterprise-hash": "10006",
        "access-token": token,
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wxe11089c85860ec02/34/page-frame.html",
        "accept-language": "zh-CN,zh;q=0.9"
    }

def sign(token):
    url = "https://vip.ixiliu.cn/mp/sign/applyV2"
    headers = get_headers(token)

    try:
        response = requests.get(url, headers=headers).json()
        return response
    except requests.RequestException as e:
        return {"status": 500, "message": f"请求错误: {e}"}

def lottery(token):
    url = "https://vip.ixiliu.cn/mp/activity.lottery/draw"
    headers = get_headers(token)
    params = {
        "snId": "381955713996608",
        "channelSn": "0"
    }

    try:
        response = requests.get(url, headers=headers, params=params).json()
        return response
    except requests.RequestException as e:
        return {"status": 500, "message": f"请求错误: {e}"}

def process_response(response):
    if response["status"] == 200:
        prize_name = response['data']['prize']['prize_name']
        return f"😃抽奖成功： {prize_name}"
    else:
        return f"😣抽奖失败： {response['message']}"

if __name__ == '__main__':
    TOKEN = os.getenv("dls")
    if not TOKEN:
        print("😖未检测到环境变量dls")
        exit(1)

    tokenList = TOKEN.split("&")
    jg = ""  # 初始化结果信息
    sign_results = ""  # 用于保存签到结果

    for index, token in enumerate(tokenList):
        print(f"-------- 第[{index + 1}]个账号 --------")
        
        # 先请求签到
        sign_response = sign(token)
        if sign_response["status"] == 200:
            sign_results += f"账号[{index + 1}] 签到成功！\n"
            print(f"账号[{index + 1}] 签到成功！")
        else:
            sign_results += f"账号[{index + 1}] 签到失败： {sign_response['message']}\n"
            print(f"账号[{index + 1}] 签到失败： {sign_response['message']}")
        
        # 然后进行抽奖
        response = lottery(token)
        lottery_result = process_response(response)
        jg += f"账号[{index + 1}] {lottery_result}\n"
        print(f"账号[{index + 1}] {lottery_result}")

        time.sleep(2)  # 延迟2秒，避免请求过于频繁

    # 将签到结果和抽奖结果一并发送
    send('杜蕾斯会员中心', f"{sign_results}\n{jg}")