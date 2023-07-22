import requests
import json
from src.config4chatbot import *
from pprint import pprint
from pymongo import MongoClient
import time
import re
import copy

class ChatBot:
    def __init__(self, system_content, max_round, whoami, mgdb_url=None):
        self.my_proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }

        self.system_content = system_content
        self.max_round = max_round
        self.msg_dict = dict()
        # 创建 MongoDB 客户端
        self.db_client = MongoClient(mgdb_url) if mgdb_url is not None else None
        self.whoami = whoami

    def get_msg_list(self, left_wcid):
        msg_list = self.msg_dict.setdefault((left_wcid, self.whoami), list())
        if len(msg_list) == 0:
            msg_list.append({"role": "system", "content": self.system_content})
            # load chat history from db if db_client is not None
            if self.db_client is not None:
                chat_history = self.get_chat_history(left_wcid)
                msg_list.extend(chat_history[-self.max_round * 2:])
        return msg_list

    def set_system_content(self, content, left_wcid):
        msg_list = self.get_msg_list(left_wcid)
        msg_list[0] = {"role": "system", "content": content}
    
    def clear_chat_history(self, left_wcid):
        msg_list = self.get_msg_list(left_wcid)
        del msg_list[1:]
        return msg_list

    def get_chat_history(self, left_wcid):
        '''
        history: a list of chat content
        {"role": "user", "content": message}  # 用户信息
        {"role": "assistant", "content": message}  # chatbot的回复信息
        '''
        assert self.db_client is not None, "db_client is None, please set mgdb_url when init ChatBot"
        db = self.db_client["wechat"]
        collection = db["chat_history"]
        history = collection.find_one({"left_wcid": left_wcid, "right_wcid": self.whoami})
        chat_history = history["chat_history"]
        # transform items in chat_history, content = f"{content} ({time})"
        for i, msg in enumerate(chat_history):
            if "time" in msg:
                chat_history[i]["content"] = f"{msg['content']} ({msg['time']})"
                del chat_history[i]["time"]
        return chat_history
    
    def sync_msg(self, msg, left_wcid):
        assert self.db_client is not None, "db_client is None, please set mgdb_url when init ChatBot"
        db = self.db_client["wechat"]
        collection = db["chat_history"]
        history = collection.find_one({"left_wcid": left_wcid, "right_wcid": self.whoami})
        chat_history = history["chat_history"]
        chat_history.append(msg)
        collection.update_one({"left_wcid": left_wcid, "right_wcid": self.whoami}, {"$set": {"chat_history": chat_history}})

    def add_msg(self, content, role, left_wcid, sync_to_db=False):
        # time: "2021-01-01 00:00:00"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        content = f"{content} ({current_time})"
        new_msg = {"role": role, "content": content}
        self.get_msg_list(left_wcid).append(new_msg)

        # pick out the time
        msg_w_time = copy.deepcopy(new_msg)
        msg_w_time["time"] = current_time
        # del the time in content by regexp
        msg_w_time["content"] = re.sub(r"\s\(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\)", "", content)
        if sync_to_db and self.db_client is not None:
            self.sync_msg(msg_w_time, left_wcid)
        return msg_w_time

    def user_send(self, user_content, left_wcid, rpl_model="gpt-3.5-turbo"):
        # msg_list = self.get_msg_list(left_wcid)
        # msg_list.append({"role": "user", "content": user_content})
        user_msg = self.add_msg(user_content, "user", left_wcid)
        data = {
            "model": rpl_model,
            "messages": self.get_msg_list(left_wcid),
            "temperature": 0.7
        }

        api = "https://api.openai.com/v1/chat/completions"

        message = "我现在有点事 一会儿再找我吧"
        num_of_tokens = len(message)
        try:
            response = requests.post(api, headers=self.headers, data=json.dumps(data), proxies=self.my_proxies)
            if response.status_code == 200:
                response = response.json()
                message = response["choices"][0]["message"]["content"]
                num_of_tokens = response['usage']['total_tokens']
            else:
                print(f"Request failed with status code {response.status_code}")
                import pdb; pdb.set_trace()
        except Exception as e:
            print("Request failed with exception")
            print(e)
        
        sync_to_db = False
        if self.db_client is not None:
            self.sync_msg(user_msg, left_wcid)
            sync_to_db = True
        self.add_msg(message, "assistant", left_wcid, sync_to_db=sync_to_db)

        print(f"============ left: {left_wcid}, right: {self.whoami}==================")
        msg_list = self.get_msg_list(left_wcid)
        pprint(msg_list)
        
        # 当消息轮次超过max_round时，删除前两条消息（保留第一条system的消息）
        if len(msg_list) > self.max_round * 2 + 1:
            del msg_list[1:3]
        return message, num_of_tokens
if __name__ == "__main__":
    pass