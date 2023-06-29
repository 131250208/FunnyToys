import requests
import json
import logging
from PIL import Image
from io import BytesIO
from pprint import pprint
logging.getLogger().setLevel(logging.INFO)
from flask import Flask, request
from pprint import pprint
from chatgpt3 import ChatBot
import re
from src.config4chatbot import *
        
class WeChatBot():
    def __init__(self) -> None:
        self.api_domain = EMANAGER_API_DOMAIN
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.emanager_account = None
        self.wid = None

    def login_emanager(self, account, password):
        api = self.api_domain + "/member/login"
        data = {
            "account": account,
            "password": password
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        
        res_json = response.json()
        if res_json["code"] == "1000":
            self.headers["Authorization"] = res_json["data"]["Authorization"]
            self.emanager_account = account
            return True
        else:
            logging.warning(res_json)
            return False
    
    def offline(self, wcid_list):
        api = self.api_domain + "/member/offline"
        data = {
            "account": self.emanager_account,
            "wcids": wcid_list
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        print(res_json)
    
    def get_qrcode(self, ttuid, wcid=""):
        api = self.api_domain + "/localIPadLogin"
        data = {
            "wcId": wcid,
            "ttuid": ttuid
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            self.wid = res_json["data"]["wId"]
            if self.download_and_open_image(res_json["data"]["qrCodeUrl"], "/root/project/chatbot/src/qrCodeUrl.jpg"):
                return True
            else:
                return False
        else:
            logging.warning(res_json)
            return False

    def login_wechat(self, verify_code=None):
        api = self.api_domain + "/getIPadLoginInfo"
        data = {
            "wId": self.wid
        }
        if verify_code is not None:
            data["verifyCode"] = verify_code

        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            return res_json["data"]
        else:
            logging.warning(res_json)
            return None
    
    def init_address_list(self):
        api = self.api_domain + "/initAddressList"
        data = {
            "wId": self.wid
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            logging.info(res_json["data"])
            return res_json["data"]
        else:
            logging.warning(res_json)
            return None
    
    def get_address_list(self):
        api = self.api_domain + "/getAddressList"
        data = {
            "wId": self.wid
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            return res_json["data"]
        else:
            logging.warning(res_json)
            return None
        
    def get_address_list(self):
        api = self.api_domain + "/getAddressList"
        data = {
            "wId": self.wid
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            return res_json["data"]
        else:
            logging.warning(res_json)
            return None
    
    def download_and_open_image(self, url, sv_path):
        # 发送GET请求下载图像数据
        response = requests.get(url)
        
        # 检查响应状态码是否为成功
        if response.status_code == 200:
            # 将图像数据读取为字节流
            image_data = response.content
            with open(sv_path, 'wb') as file:
                file.write(image_data)

            # 使用PIL库打开图像
            image = Image.open(BytesIO(image_data))

            # 显示图像
            image.show()
            logging.info("请扫码登录")
            return True
        else:
            logging.warning("无法下载图像")
            return False
        
    def set_callback_url(self, http_url):
        api = self.api_domain + "/setHttpCallbackUrl"
        data = {
            "httpUrl": http_url,
            "type": 2
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            return True
        else:
            logging.warning(res_json)
            return False
    
    def sent_text(self, left_wcid, text):
        api = self.api_domain + "/sendText"
        data = {
            "wId": self.wid,
            "wcId": left_wcid,
            "content": text
        }
        response = requests.post(api, headers=self.headers, data=json.dumps(data))
        res_json = response.json()
        if res_json["code"] == "1000":
            logging.info(res_json)
            return True
        else:
            logging.warning(res_json)
            return False

def listen_and_rpl():
    rsm_app = Flask(__name__)
    system_content = "你要进行日常聊天，不要回复太长的话，不要用书面化语言，请用日常口语化的表达，不要说你是AI语言模型、小助手或者机器人，不是一个真实的人类，你的任务是扮演一个普通人类进行聊天"
    chat_agent = ChatBot(system_content, max_round=10)
    
    call_back_url = "http://124.71.45.196:5000/api/get_msg"
    bot = WeChatBot()

    # wcid
    # betalau wxid_m9lhdlutblw812
    if bot.login_emanager(EMANAGER_ACCOUNT, EMANAGER_PASSWORD):
        ttuid = "a7689d8b-25ba-4ca8-9ca8-c09c19b60d0e" # input("ttuid:")
        if bot.get_qrcode(ttuid, "wxid_m9lhdlutblw812"):
            login_success_info = bot.login_wechat()
            pprint(login_success_info)

    @rsm_app.route('/api/get_msg', methods=['POST'])
    def process_post_request():
        data = request.get_json()  # 获取POST请求中的JSON数据
        if data["messageType"] == "60001":
            send_txt = data["data"]["content"]
            fromUser_wcid = data["data"]["fromUser"]
            pprint(data)
            # 调用chatgpt回复
            if not data["data"]["self"] and BOT_KEYWORD in send_txt:
                send_txt = re.sub(BOT_KEYWORD, "", send_txt)
                res = chat_agent.user_send(send_txt)
                if res is not None:
                    rpl, toks_num = res
                else:
                    rpl = "请求失败了，请稍后再试..."
                bot.sent_text(fromUser_wcid, rpl)
        return data
    
    rsm_app.run(host='0.0.0.0', port=5000)
    bot.set_callback_url(call_back_url)

if __name__ == '__main__':
    listen_and_rpl()
    # import requests
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    # res = requests.post("http://124.71.45.196:5000/api/get_msg", data=json.dumps({"hello": "world!"}), headers=headers)
    # print(res.json())


    # while True:
    #     cml = input("command_line:")
    #     if cml == "quit":
    #         bot.offline(["wxid_m9lhdlutblw812"])
    #     elif "send:" in cml:
    #         _, wcid, text = cml.split(":")
    #         bot.sent_text(wcid, text)
    #     elif cml == "init address":
    #         bot.init_address_list()
    #     elif cml == "get_address":
    #         res = bot.get_address_list()
    #         pprint(res)

