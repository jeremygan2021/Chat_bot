from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory,RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import random
from lib.PyOfficeRobot.core.WeChatType import WeChat
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.chat_message_histories import ChatMessageHistory




class Chat_memory:
    def __init__(self,function):
        self.wx = WeChat()
        self.chat_history = ChatMessageHistory()
        self.chat = ChatOpenAI(api_key="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",
                           base_url='http://openai.tangledup-ai.com/v1', model="gpt-4-turbo",
                           temperature=0.5) # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo
        self.llm3 =llm3 = ChatOpenAI(api_key="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",
                           base_url='http://openai.tangledup-ai.com/v1', model="gpt-3.5-turbo-0125",
                           temperature=0.4) # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

        self.llm_zhipu = ChatZhipuAI(temperature=0.6,
                        model="glm-4",  # glm-4,glm-3
                        zhipuai_api_key="f6d295b3ae2a9d9a8b05ac7efbb7e022.5NXLJkBRDSe5pkTP", )

        self.prompt = ChatPromptTemplate.from_messages([
        ("system", function),
        ("user", "{input}")])

        self.memory_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                function,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

        self.Ask_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你将要判断输入的回复的文字里是否有优秀学员的'名字'和'组别'，如果两者都有就return Ture，否则就return False，只输出Ture或False。"),
            ("user", "{input}")])
        self.ask_chain = self.Ask_prompt | self.llm3
        self.chain = self.prompt | self.chat
        self.memory_chain = self.memory_prompt | self.chat


    def summarize_messages(self,chain_input):
        stored_messages = self.chat_history.messages
        if len(stored_messages) == 0:
            return False
        summarization_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    "Distill the above chat messages into a single summary message. Include as many specific details as you can.中文输出",
                ),
            ]
        )
        summarization_chain = summarization_prompt | self.chat

        summary_message = summarization_chain.invoke({"chat_history": stored_messages})

        self.chat_history.clear()

        self.chat_history.add_message(summary_message)

        return True



    def chat_by_langchain_memory(self,who):
        self.wx.GetSessionList()  # 获取会话列表
        self.wx.ChatWith(who)  # 打开`who`的聊天窗口
        temp_msg = None
     # 初始化存储消息的列表
        while True:
            try:
                friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][1]  # 获取朋友的名字和发送的信息
                if (friend_name == who) and (receive_msg != temp_msg):
                    """
                    条件：
                    朋友名字正确:(friend_name == who)
                    不是上次的对话:(receive_msg != temp_msg)
                    """
                    print(f'【{who}】发送：【{receive_msg}】')
                    temp_msg = receive_msg
                    self.chat_history.add_user_message(receive_msg)  # 将收到的消息存储到chat_history中

                    chain_message_history = RunnableWithMessageHistory(
                        self.memory_chain,
                        lambda session_id: self.chat_history,
                        input_messages_key="input",
                        history_messages_key="chat_history",
                    )

                    reply_msg = chain_message_history.invoke(
                    {"input": receive_msg},
                  {"configurable": {"session_id": "unused"}},).content
                    print(reply_msg)
                    self.chat_history.add_ai_message(reply_msg)  # 将发送的消息存储到chat_history中
                    time.sleep(random.randint(0, 3))  # 随机等待1-3秒
                    self.wx.SendMsg(reply_msg, who)# 向`who`发送消息
                    print(self.chat_history.messages)
                    return reply_msg
                    # 在store_msg中存储收到的消息和发送的消息
            except:
                pass


    def chat_by_langchain_memory_summary(self,who):
        self.wx.GetSessionList()  # 获取会话列表
        self.wx.ChatWith(who)  # 打开`who`的聊天窗口
        temp_msg = None

     # 初始化存储消息的列表
        while True:
            try:
                friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][1]  # 获取朋友的名字和发送的信息
                if (friend_name == who) and (receive_msg != temp_msg):
                    """
                    条件：
                    朋友名字正确:(friend_name == who)
                    不是上次的对话:(receive_msg != temp_msg)
                    """
                    print(f'【{who}】发送：【{receive_msg}】')
                    temp_msg = receive_msg
                    self.chat_history.add_user_message(receive_msg)  # 将收到的消息存储到chat_history中

                    chain_message_history = RunnableWithMessageHistory(
                        self.memory_chain,
                        lambda session_id: self.chat_history,
                        input_messages_key="input",
                        history_messages_key="chat_history",
                    )

                    print(len(self.chat_history.messages))



                    if len(self.chat_history.messages) <= 20:
                        print("正常对话")
                        reply_msg = chain_message_history.invoke(
                            {"input": receive_msg},
                            {"configurable": {"session_id": "unused"}}, ).content
                        self.chat_history.add_ai_message(reply_msg)
                        print(reply_msg)
                        self.wx.SendMsg(reply_msg, who)
                        print(len(self.chat_history.messages))
                        print(self.chat_history.messages)
                        return reply_msg


                    else:
                        chain_with_summarization = (
                                RunnablePassthrough.assign(messages_summarized=self.summarize_messages)
                                | chain_message_history
                        )
                        print('总结历史')
                        reply_msg = chain_with_summarization.invoke(
                            {"input": receive_msg},
                            {"configurable": {"session_id": "unused"}}, ).content
                        print(reply_msg)
                        time.sleep(random.randint(0, 3))  # 将发送的消息存储到chat_history中
                        self.wx.SendMsg(reply_msg, who)  # 向`who`发送消息
                        print(self.chat_history.messages)
                        print(len(stored_messages))
                        print(self.chat_history.messages)
                        return reply_msg
                    # 在store_msg中存储收到的消息和发送的消息
            except:
                pass




    def chat_by_langchain_memory_summary_detect_for_name(self,who,null_group):
        self.wx.GetSessionList()  # 获取会话列表
        self.wx.ChatWith(who)  # 打开`who`的聊天窗口
        temp_msg = None
        Ask_prompt_A = ChatPromptTemplate.from_messages([
            ("system",
             f"你将要判断输入的回复的文字里是否有[{null_group}]的优秀学员的'名字'和'组别'"
             f"主要看最新回复信息，也稍微观察历史记录,有小组和名字两个是必要的，有这两个就是Ture，否则就return False，只输出Ture或False。"),
            ("user", "{input}")])
        Ask_chain_A = Ask_prompt_A | self.llm_zhipu
     # 初始化存储消息的列表
        while True:
            try:
                friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][1]  # 获取朋友的名字和发送的信息
                if (friend_name == who) and (receive_msg != temp_msg):
                    """
                    条件：
                    朋友名字正确:(friend_name == who)
                    不是上次的对话:(receive_msg != temp_msg)
                    """
                    print(f'【{who}】发送：【{receive_msg}】')
                    # print(self.chat_history.messages[1])
                    whole_msg = "回复信息：【" + receive_msg + "】 历史对话：" + str(self.chat_history.messages)
                    print("识别内容：" + whole_msg)
                    detect = Ask_chain_A.invoke({"input": whole_msg }).content
                    print(f"意图检测为：{detect}")
                    if detect == "True":
                        print("打破循环")
                        self.wx.SendMsg_hotkey("好的，已经收到你的小组消息，请稍等正在保存---》》》", who)
                        return receive_msg
                        break  # 当detect为"True"时，跳出循环
                    temp_msg = receive_msg
                    self.chat_history.add_user_message(receive_msg)  # 将收到的消息存储到chat_history中

                    chain_message_history = RunnableWithMessageHistory(
                        self.memory_chain,
                        lambda session_id: self.chat_history,
                        input_messages_key="input",
                        history_messages_key="chat_history",
                    )

                    print(f"存储字符为：{len(self.chat_history.messages)}")



                    if len(self.chat_history.messages) <= 10:
                        print("正常对话")
                        reply_msg = chain_message_history.invoke(
                            {"input": f"告知对方这段对话没有通过语义识别，缺少了关键信息：{receive_msg}，少了{null_group}的姓名，组别，日期还是推优原因，并告知对方重新回答。"},
                            {"configurable": {"session_id": "unused"}}, ).content
                        self.chat_history.add_ai_message(reply_msg)
                        print(reply_msg)
                        self.wx.SendMsg_hotkey(reply_msg, who)
                        print(f"存储字符为：{len(self.chat_history.messages)}")
                        print(self.chat_history.messages)



                    else:
                        chain_with_summarization = (
                                RunnablePassthrough.assign(messages_summarized=self.summarize_messages)
                                | chain_message_history
                        )
                        print('总结历史')
                        reply_msg = chain_with_summarization.invoke(
                            {"input": receive_msg},
                            {"configurable": {"session_id": "unused"}}, ).content
                        print(reply_msg)
                        time.sleep(random.randint(0, 3))  # 将发送的消息存储到chat_history中
                        self.wx.SendMsg_hotkey(reply_msg, who)  # 向`who`发送消息
                        print(self.chat_history.messages)
                        print(f"存储字符为：{len(self.chat_history.messages)}")
                        print(self.chat_history.messages)

                    # 在store_msg中存储收到的消息和发送的消息

            except:
                pass

    def chat_by_langchain_memory_summary_detect_for_purse(self,who,purse):
        self.wx.GetSessionList()  # 获取会话列表
        self.wx.ChatWith(who)  # 打开`who`的聊天窗口
        temp_msg = None
        Ask_prompt_A = ChatPromptTemplate.from_messages([
            ("system",
             f"你将要判断输入的回复的文字里是否有[{purse}]的目的"
             f"主要看最新回复信息，也稍察历史记录,有就是Ture，否则就return False，只输出Ture或False。"),
            ("user", "{input}")])
        Ask_chain_A = Ask_prompt_A | self.llm_zhipu
     # 初始化存储消息的列表
        while True:
            try:
                friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][1]  # 获取朋友的名字和发送的信息
                if (friend_name == who) and (receive_msg != temp_msg):
                    """
                    条件：
                    朋友名字正确:(friend_name == who)
                    不是上次的对话:(receive_msg != temp_msg)
                    """
                    print(f'【{who}】发送：【{receive_msg}】')
                    # print(self.chat_history.messages[1])
                    whole_msg = "回复信息：【" + receive_msg + "】 历史对话：" + str(self.chat_history.messages)
                    print("识别内容：" + whole_msg)
                    detect = Ask_chain_A.invoke({"input": whole_msg }).content
                    print(f"意图检测为：{detect}")
                    if detect == "True":
                        print("打破循环")

                        self.wx.SendMsg_hotkey("好的，已经收到你的消息，请稍等正在保存---》》》", who)
                        return receive_msg
                        break  # 当detect为"True"时，跳出循环
                    temp_msg = receive_msg
                    self.chat_history.add_user_message(receive_msg)  # 将收到的消息存储到chat_history中

                    chain_message_history = RunnableWithMessageHistory(
                        self.memory_chain,
                        lambda session_id: self.chat_history,
                        input_messages_key="input",
                        history_messages_key="chat_history",
                    )

                    print(f"存储字符为：{len(self.chat_history.messages)}")

                    if len(self.chat_history.messages) <= 10:
                        print("正常对话")
                        reply_msg = chain_message_history.invoke(
                            {"input": f"告知对方：你的来意，并用不被察觉的方法遇到他说出{purse}。，只输出对话"},
                            {"configurable": {"session_id": "unused"}}, ).content
                        self.chat_history.add_ai_message(reply_msg)
                        print(reply_msg)
                        self.wx.SendMsg_hotkey(reply_msg, who)
                        print(f"存储字符为：{len(self.chat_history.messages)}")
                        print(self.chat_history.messages)



                    else:
                        chain_with_summarization = (
                                RunnablePassthrough.assign(messages_summarized=self.summarize_messages)
                                | chain_message_history
                        )
                        print('总结历史')
                        reply_msg = chain_with_summarization.invoke(
                            {"input": receive_msg},
                            {"configurable": {"session_id": "unused"}}, ).content
                        print(reply_msg)
                        time.sleep(random.randint(0, 3))  # 将发送的消息存储到chat_history中
                        self.wx.SendMsg_hotkey(reply_msg, who)  # 向`who`发送消息
                        print(self.chat_history.messages)
                        print(f"存储字符为：{len(self.chat_history.messages)}")
                        print(self.chat_history.messages)

                    # 在store_msg中存储收到的消息和发送的消息

            except:
                pass


if __name__ == '__main__':
    null_group = "三组"
    chat = Chat_memory(function=f"你在寻找[{null_group}]优秀学员的'名字'和'组别'的信息,要是没有就继续追问，并引导对方说出[{null_group}]优秀学员和所在小组，并强调要把组别和姓名以及日期发在一条信息里,而不是其他组")
    #AI.chat_by_langchain_memory('甘昭泉')
    # AI.chat_by_langchain_memory_summary('甘昭泉')
    chat.chat_by_langchain_memory_summary_detect_for_name('甘昭泉',null_group)

