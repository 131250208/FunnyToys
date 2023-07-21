from bs4 import BeautifulSoup
from glob import glob
import re
from tqdm import tqdm
import json
from pymongo import MongoClient

def parse_msg_div(msg_div):
    if "chat-notice" in msg_div.attrs["class"]:
        msg_text = msg_div.text.strip()
        return {
            "type": "notice",
            "msg": msg_text
        }
    right_chat = True if "right" in msg_div.attrs["class"] else False
    avatar_src = msg_div.find("img", class_="avatar").attrs["src"]
    wcid = avatar_src.split("/")[-1].split(".")[0]
    dspname_span = msg_div.find("span", class_="dspname")
    name_time = dspname_span.parent.text
    dspname = dspname_span.text
    time = re.sub(re.escape(dspname), "", name_time).strip()
    content_box = msg_div.find("div", class_="content-box")
    msg_text = content_box.text.strip()
    if msg_text == "" and content_box.find("img"):
        msg_text = "[图片]" 
    
    return {
        "type": "chat_msg",
        "right": right_chat,
        "wcid": wcid,
        "dspname": dspname,
        "time": time,
        "msg": msg_text,
    }

def trans_to_chatgpt_style(chat_history):
    new_chat_history = []
    for msg in chat_history:
        new_msg = {}
        if msg["type"] == "chat_msg":
            if type(msg["msg"]) is list:
                msg["msg"] = "聊天记录:\n" + "\n".join([f"{msg['dspname']} {msg['time']}\n{msg['msg']}" for msg in msg["msg"]])
            new_msg = {"role": "user" if not msg["right"] else "assistant", "content": msg["msg"], "time": msg["time"]}
        elif msg["type"] == "notice":
            new_msg = {"role": "system", "content": msg["msg"]}
        new_chat_history.append(new_msg)
    return new_chat_history


# MongoDB 连接字符串
uri = 'mongodb://localhost:27017'

# 创建 MongoDB 客户端
client = MongoClient(uri)

chat_data = list()

for path in glob("/root/project/FunnyToys/ToyFactory/chatbot/src/wechat_records/wyc/html/*.html"):
    html_doc = open(path, "r", encoding="utf-8")
    soup = BeautifulSoup(html_doc, "lxml")
    div_list = soup.find_all("div", class_="msg")
    file_name = path.split('/')[-1]

    chat_history = []
    chat_record_region = False
    inner_chat_records = []
    for msg_div in tqdm(div_list, desc=path.split("/")[-1]):
        if "fmsgtag" in msg_div.attrs["class"] and "<< " in msg_div.text:
            chat_record_region = True
            continue
        elif "fmsgtag" in msg_div.attrs["class"] and "结束 >>" in msg_div.text:
            chat_record_region = False
            chat_history[-1]["msg"] = inner_chat_records
            inner_chat_records = []
            continue
    
        if chat_record_region:
            inner_chat_records.append(parse_msg_div(msg_div))
        else:
            chat_history.append(parse_msg_div(msg_div))
    
    notices = [msg for msg in chat_history if msg["type"] == "notice"]
    left_wcid_list = {msg["wcid"] for msg in chat_history if msg["type"] == "chat_msg" and msg["right"] == False}
    right_wcid_list = {msg["wcid"] for msg in chat_history if msg["type"] == "chat_msg" and msg["right"] == True}

    # wcid = max(set(wcid_list), key=wcid_list.count)
    if len(left_wcid_list) != 1 or len(right_wcid_list) != 1:
        print("========= wcid list != 1 =========")
        print(path)
        print("left: f{left_wcid_list}, right: {right_wcid_list}}")
        # if file_name == "冯琳.html":
        #     print("冯琳")
        #     import pdb; pdb.set_trace()
    else:
        left_wcid = left_wcid_list.pop()
        right_wcid = right_wcid_list.pop()
        chat_history = trans_to_chatgpt_style(chat_history)
        chat_data.append({"left_wcid": left_wcid, "right_wcid": right_wcid, "chat_history": chat_history, "type": "1v1", "left_name": file_name.split(".")[0]})
        # with open("project/FunnyToys/ToyFactory/chatbot/src/wechat_records/wyc/chat_hist_json/{}.json".format(wcid), "w", encoding="utf-8") as file_out:
        #     json.dump(chat_history, file_out, ensure_ascii=False)
        # print(path.split("/")[-1], len(chat_history), len(notices), len(wcid_list))

print(len(chat_data))

# 连接到 MongoDB
with client:
    for item in chat_data:
        left_wcid = item["left_wcid"]
        right_wcid = item["right_wcid"]
        # if item["left_name"] == "冯琳": # wxid_55hlyad2yypj11
        #     import pdb; pdb.set_trace()
        # 指定要使用的数据库和集合
        database = client['wechat']
        collection = database['chat_history']
        # 插入数据
        left_right = {"left_wcid": left_wcid, "right_wcid": right_wcid}
        count = collection.count_documents(left_right)
        if count == 0:
            collection.insert_one(item)
            print(f"{item['left_name']} is not in database and inserted just now.")
        else:
            print(f"{item['left_name']} is already in database.")
