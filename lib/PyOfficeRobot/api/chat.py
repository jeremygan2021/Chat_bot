import datetime
import os
import time


import porobot as porobot
import schedule

from PyOfficeRobot.core.WeChatType import WeChat
from PyOfficeRobot.lib.decorator_utils.instruction_url import instruction
from zhipuai import ZhipuAI
from pyautogui import hotkey
import pyautogui


def listen_click_muse(picture_path,confH=0.86):
    while True:
        try:
            hold_pos = pyautogui.locateOnScreen(picture_path, grayscale=True,confidence=confH)
            if hold_pos is not None:
                print(f"图片被检测到！{picture_path}")
                pyautogui.doubleClick(hold_pos.left + hold_pos.width / 2, hold_pos.top + hold_pos.height / 2)
                break  # 如果找到图片，则跳出循环
        except Exception as e:
            print(f"图片未监测到：{e}")
            # 在这里处理错误，例如记录日志或进行其他操作
        time.sleep(1)  # 暂停1秒钟，避免密集循环检查

    # 图片已经找到，计算中心位置并移动鼠标点击
    goto_pos = pyautogui.center(hold_pos)
    pyautogui.moveTo(goto_pos, duration=0.3)
    pyautogui.click()
    # 在这里执行其他命令

def find_img(image_path):
    image_location = pyautogui.locateOnScreen(image_path)
    if image_location is not None:
        print("找到了！")
        return True
    else:
        print("未找到。")
        return False

wx = WeChat()

def check_pepole(who: str,image_path=r"D:\AI_Machine_learning\chatgpt-on-wechat-master\data\dj.png") -> None:
    hotkey('ctrl', 'a')

    # 获取会话列表
    wx.GetSessionList()
    wx.Search_hotkey(who)  # 打开`who`聊天窗口
    listen_click_muse(image_path)
    time.sleep(5)
    if find_img(r"D:\AI_Machine_learning\chatgpt-on-wechat-master\data\txl.png"):
        return True
    return False
    
 



def send_message_hotkey(who: str, message: str) -> None:
    """
    给指定人，发送一条消息
    :param who:
    :param message:
    :return:
    """

    # 获取会话列表
    wx.GetSessionList()
    wx.ChatWith(who)  # 打开`who`聊天窗口
    # for i in range(10):
    wx.SendMsg_hotkey(message, who)  # 向`who`发送消息：你好~

# @act_info(ACT_TYPE.MESSAGE)

def send_message(who: str, message: str) -> None:
    """
    给指定人，发送一条消息
    :param who:
    :param message:
    :return:
    """

    # 获取会话列表
    wx.GetSessionList()
    wx.ChatWith(who)  # 打开`who`聊天窗口
    # for i in range(10):
    wx.SendMsg(message, who)  # 向`who`发送消息：你好~



def chat_by_keywords(who: str, keywords: str):
    wx.GetSessionList()  # 获取会话列表
    wx.ChatWith(who)  # 打开`who`聊天窗口
    temp_msg = ''
    while True:
        try:
            friend_name, receive_msg = wx.GetAllMessage[-1][0], wx.GetAllMessage[-1][1]  # 获取朋友的名字、发送的信息
            if (friend_name == who) & (receive_msg != temp_msg) & (receive_msg in keywords.keys()):
                """
                条件：
                朋友名字正确:(friend_name == who)
                不是上次的对话:(receive_msg != temp_msg)
                对方内容在自己的预设里:(receive_msg in kv.keys())
                """

                temp_msg = receive_msg
                wx.SendMsg(keywords[receive_msg], who)  # 向`who`发送消息
        except:
            pass



def receive_message(who='文件传输助手', txt='userMessage.txt', output_path='./'):
    wx.GetSessionList()  # 获取会话列表
    wx.ChatWith(who)  # 打开`who`聊天窗口
    while True:
        friend_name, receive_msg = wx.GetAllMessage[-1][0], wx.GetAllMessage[-1][1]  # 获取朋友的名字、发送的信息
        current_time = datetime.datetime.now()
        cut_line = '^^^----------^^^'
        print('--' * 88)
        with open(os.path.join(output_path, txt), 'a+') as output_file:
            output_file.write('\n')
            output_file.write(cut_line)
            output_file.write('\n')
            output_file.write(str(current_time))
            output_file.write('\n')
            output_file.write(str(friend_name))
            output_file.write('\n')
            output_file.write(str(receive_msg))
            output_file.write('\n')



def send_message_by_time(who, message, time):
    schedule.every().day.at(time).do(send_message, who=who, message=message)
    while True:
        schedule.run_pending()





def chat_by_zhipu_RAG(res,temperature=0.6):
    client = ZhipuAI(api_key="f6d295b3ae2a9d9a8b05ac7efbb7e022.5NXLJkBRDSe5pkTP")
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": res},
        ],
        tools=[
            {
                "type": "retrieval",
                "retrieval": {
                    "knowledge_id": "1790405075647205376",
                    "prompt_template": "你是首富思维的客服小助手，从文档\n\"\"\"\n{{knowledge}}\n\"\"\"\n中找问题\n\"\"\"\n{{question}}\n\"\"\"\n的答案，找到答案就仅使用文档语句回答问题，找不到答案就用自身知识回答并且告诉用户该信息不是来自文档。\n不要复述问题，直接输出回答。"
                }
            }
        ],
        stream=True,
    )
    result = ""
    for chunk in response:
        for char in chunk.choices[0].delta.content:
            print(char, end='', flush=True)
            result += char
        result += ""
    print(result)

    reply_msg = f"{friend_name}你好，以下是你的检索答案：" + result

    wx.SendMsg_hotkey(reply_msg, who="测试机器人")  # 向`who`发送消息




def chat_robot(who):
    wx.GetSessionList()  # 获取会话列表
    wx.ChatWith(who)  # 打开`who`聊天窗口
    temp_msg = None
    while True:
        try:
            friend_name, receive_msg = wx.GetAllMessage[-1][0], wx.GetAllMessage[-1][1]  # 获取朋友的名字、发送的信息
            if (friend_name == who) & (receive_msg != temp_msg):
                """
                条件：
                朋友名字正确:(friend_name == who)
                不是上次的对话:(receive_msg != temp_msg)
                对方内容在自己的预设里:(receive_msg in kv.keys())
                """
                print(f'【{who}】发送：【{receive_msg}】')
                temp_msg = receive_msg
                reply_msg = porobot.normal.chat(receive_msg)
                wx.SendMsg(reply_msg, who)  # 向`who`发送消息
        except:
            pass




