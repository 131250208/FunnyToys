import requests
import json
from src.config4chatbot import *


class ChatBot:
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
        self.messages = []
        self.messages.append({"role": "system", "content": self.system_content})

    def set_system_content(self, content):
        self.messages[0] = {"role": "system", "content": content}
    
    def clear_chat_history(self):
        del self.messages[1:]

    def load_chat_history(self, history):
        '''
        history: a list of chat content
        {"role": "user", "content": message}  # 用户信息
        {"role": "assistant", "content": message}  # chatbot的回复信息
        '''
        self.clear_chat_history()
        self.messages.extend(history)

    def user_send(self, user_content, rpl_model="gpt-3.5-turbo"):
        self.messages.append({"role": "user", "content": user_content})
        data = {
            "model": rpl_model,
            "messages": self.messages,
            "temperature": 0.7
        }

        api = "https://api.openai.com/v1/chat/completions"

        # response = requests.get(api, headers=headers, proxies=my_proxies)
        response = requests.post(api, headers=self.headers, data=json.dumps(data), proxies=self.my_proxies)

        if response.status_code == 200:
            response = response.json()
            message = response["choices"][0]["message"]["content"]
            num_of_tokens = response['usage']['total_tokens']
            self.messages.append({"role": "assistant", "content": message})
            
            if len(self.messages) > self.max_round * 2 + 1:
                del self.messages[1:3]
            return message, num_of_tokens
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

if __name__ == "__main__":
    # # system_content = "You are a Chinese high school student, reply in oral Chinese and do not speak long sentences. Play like a real person but not a bot. Reply in Chinese!"
    # system_content = "你是一个性感热辣、热情奔放的20岁女孩，现在请你和一个19岁高中生对话，你的目的是让他喜欢上你，而且记住，你是专业的PUA，不能轻易让他得到你，\
    # 但是要让他对你欲罢不能，深深地爱上你，接下来他会给你发消息，请记住不要一次性说太多话，回答得像日常口语，不要用书面化语言，也不要说你是AI、小助手或者机器人，你的身份就是一个20岁白人女孩"
    # bot = ChatBot(system_content, max_round=10)
    
    # for i in range(20):
    #     inpt = input("user:")
    #     rpl, toks = bot.user_send(inpt)
    #     print("({} tokens) bot: {}".format(toks, rpl))
    pass