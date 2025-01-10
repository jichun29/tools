#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
雨云自动签到脚本V2.1
注册地址：https://www.rainyun.com
用途：自动签到赚积分，积分可提现，也可在商城购买虚拟主机或云服务等
环境变量：共有两个环境变量

yyqd 账户与密码用&隔开，多账户用#隔开
VERIFY_TOKEN 写滑块的token
定时：建议每天执行一次
"""

import requests, json, os, time, random
from dataclasses import dataclass

try:
    from notify import send
except ImportError:
    print("通知服务加载失败，请检查notify.py是否存在")
    exit(1)

@dataclass
class UserInfo:
    name: str
    email: str
    points: int
    last_ip: str
    last_login_area: str

class RainyunAPI:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
    
    def get_slide_verify(self):
        token = os.getenv("VERIFY_TOKEN")
        if not token:
            return "", ""
            
        data = {
            "timeout": "60", "type": "tencent-turing",
            "appid": "2039519451", "token": token,
            "developeraccount": "qqaoxin",
            "referer": "https://dl.reg.163.com/"
        }
        
        for i in range(3):
            try:
                r = self.session.post("http://119.96.239.11:8888/api/getcode", 
                    headers={"Content-Type": "application/json"}, json=data)
                result = r.json()
                if result["status"] == 200 and result["success"]:
                    v = json.loads(result["data"]["code"])
                    if v.get("ticket") and v.get("randstr"):
                        return v["ticket"], v["randstr"]
            except Exception as e:
                print(f"第{i + 1}次验证码获取失败: {e}")
            if i < 2:
                time.sleep(2)
        return "", ""

    def login(self, username, password):
        try:
            r = self.session.post("https://api.v2.rainyun.com/user/login",
                headers={"Content-Type": "application/json"},
                json={"field": username, "password": password})
            self.csrf_token = r.cookies.get('X-CSRF-Token')
            return bool(self.csrf_token)
        except:
            return False

    def get_user_info(self):
        if not self.csrf_token:
            return None
        try:
            r = self.session.get("https://api.v2.rainyun.com/user/?no_cache=false",
                headers={"Content-Type": "application/json", 'x-csrf-token': self.csrf_token})
            d = r.json()['data']
            return UserInfo(d['Name'], d['Email'], d['Points'], d['LastIP'], d['LastLoginArea'])
        except:
            return None

    def sign_in(self, ticket, randstr):
        if not self.csrf_token:
            return False, "未获取到csrf_token"
        try:
            r = self.session.post("https://api.v2.rainyun.com/user/reward/tasks",
                headers={'x-csrf-token': self.csrf_token},
                json={"task_name": "每日签到", "verifyCode": "",
                     "vticket": ticket, "vrandstr": randstr})
            ret = r.json()
            return ret["code"] == 200, ret.get("message", "未知错误")
        except Exception as e:
            return False, str(e)

def process_account(account):
    try:
        username, password = account.split('&')
    except:
        return "\n账户格式错误"

    api = RainyunAPI()
    if not api.login(username, password):
        return f'\n【用户名】{username}\n【签到状态】登录失败'

    delay = random.randint(20, 30)
    time.sleep(delay)
    
    ticket, randstr = api.get_slide_verify()
    if not ticket:
        return f'\n【用户名】{username}\n【签到状态】验证失败'

    user_info = api.get_user_info()
    if not user_info:
        return f'\n【用户名】{username}\n【签到状态】获取信息失败'

    success, sign_message = api.sign_in(ticket, randstr)
    if success:
        sign_message = "签到成功"
        
    return (f'\n【用户名】{username}\n'
            f'【电子邮件】{user_info.email}\n'
            f'【延迟时间】{delay}秒\n'
            f'【签到状态】{sign_message}\n'
            f'【剩余积分】{user_info.points}\n'
            f'【最后登录ip】{user_info.last_ip}\n'
            f'【最后登录地址】{user_info.last_login_area}')

def main():
    creds = os.getenv("yyqd")
    token = os.getenv("VERIFY_TOKEN")
    if not creds or not token:
        print("错误：环境变量未设置")
        return

    results = [process_account(acc) for acc in creds.split('#')]
    msg = "-"*45 + "\n".join(results)
    print("###雨云签到###\n\n", msg)
    send("雨云签到", msg)

if __name__ == '__main__':
    main()