import requests
import json
from src.config4chatbot import *
from pprint import pprint


class ChatBot:
    DEFAULT = "default"
    def __init__(self, system_content, max_round):
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

    def get_msg_list(self, key=DEFAULT):
        msg_list = self.msg_dict.setdefault(key, [])
        if len(msg_list) == 0:
            msg_list.append({"role": "system", "content": self.system_content})
        return msg_list

    def set_system_content(self, content, key=DEFAULT):
        msg_list = self.get_msg_list(key)
        msg_list[0] = {"role": "system", "content": content}
    
    def clear_chat_history(self, key=DEFAULT):
        msg_list = self.get_msg_list(key)
        del msg_list[1:]
        return msg_list

    def load_chat_history(self, history, key=DEFAULT):
        '''
        history: a list of chat content
        {"role": "user", "content": message}  # 用户信息
        {"role": "assistant", "content": message}  # chatbot的回复信息
        '''
        msg_list = self.clear_chat_history(key)
        msg_list.extend(history)

    def get_chat_history(self, key=DEFAULT):
        return self.get_msg_list(key)[1:]
    
    def add_msg(self, content, role, key=DEFAULT):
        self.get_msg_list(key).append({"role": role, "content": content})

    def user_send(self, user_content, rpl_model="gpt-3.5-turbo", key=DEFAULT):
        msg_list = self.get_msg_list(key)
        msg_list.append({"role": "user", "content": user_content})
        data = {
            "model": rpl_model,
            "messages": msg_list,
            "temperature": 0.7
        }

        api = "https://api.openai.com/v1/chat/completions"

        # response = requests.get(api, headers=headers, proxies=my_proxies)
        response = requests.post(api, headers=self.headers, data=json.dumps(data), proxies=self.my_proxies)

        if response.status_code == 200:
            response = response.json()
            message = response["choices"][0]["message"]["content"]
            num_of_tokens = response['usage']['total_tokens']
            msg_list.append({"role": "assistant", "content": message})
            print("============ msg_list ==================")
            pprint(msg_list)
            
            if len(msg_list) > self.max_round * 2 + 1:
                del msg_list[1:3]
            return message, num_of_tokens
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

if __name__ == "__main__":
    pass