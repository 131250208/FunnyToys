from bs4 import BeautifulSoup
from glob import glob
import re

for path in glob("project/FunnyToys/ToyFactory/chatbot/src/wechat_records/wyc/*.html"):
    html_doc = open(path, "r", encoding="utf-8")
    soup = BeautifulSoup(html_doc, "lxml")
    div_list = soup.find_all("div", class_="msg")
    for msg_div in div_list:
        # 还有聊天记录的解析
        
        right_chat = True if "right" in msg_div.attrs["class"] else False
        avatar_src = msg_div.find("img", class_="avatar").attrs["src"]
        wcid = avatar_src.split("/")[-1].split(".")[0]
        dspname_span = msg_div.find("span", class_="dspname")
        name_time = dspname_span.parent.text
        dspname = dspname_span.text
        time = re.sub(dspname, "", name_time).strip()
        msg_text_span = msg_div.find("span", class_="msg-text")
        msg_text = msg_text_span.text.strip()
        if msg_text == "" and msg_text_span.find("img"):
            msg_text = "[图片]"

        print()
