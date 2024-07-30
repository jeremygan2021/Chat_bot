from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
import json
import time
import random
import csv
from datetime import datetime, timedelta
from collections import deque
from lib.PyOfficeRobot.core.WeChatType import WeChat
from langchain_community.chat_models import ChatZhipuAI
from langchain.memory import ConversationSummaryMemory, ConversationSummaryBufferMemory, \
	ConversationEntityMemory
from langchain_community.memory.kg import ConversationKGMemory
from Prompt_template import Wechat, Q_bake

from lib.pprint import pprint
# from langchain.chains.conversation.base import ConversationChain
from langchain.chains import ConversationChain
from chat_bot1 import structured_llm
import ast

import os
import sys
import config
from langchain_community.chat_message_histories import ChatMessageHistory

######################################################
# from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QPushButton
# from PyQt5.QtCore import QTimer
# from PyQt5.QtGui import QIcon
# import sys


###########################################################记忆力存储模块################################################################

current_dir = os.path.dirname(__file__)

# 生成相对路径
Memory_wechat_path = os.path.abspath(os.path.join(current_dir, 'Chat_memory', 'Memory_wechat.csv'))
Memory_Terminal_path = os.path.abspath(os.path.join(current_dir, 'Chat_memory', 'Memory_interface.csv'))

# 将当前文件目录添加到系统路径中
sys.path.append(current_dir)

we = WeChat()


# def gen_voice(content):
# 	Huogshan_TTS.gen_voice_bychat(content=content, file_name="语音_点击收听",
# 								  voice_type="zh_male_M392_conversation_wvae_bigtts")


# 湾湾小何
# 方言场景 台湾普通话
# zh_female_xiaohe_conversation_wvae_bigtts
# -
# 温暖阿虎 通用场景
# 中文
# zh_male_ahu_conversation_wvae_bigtts
# -
# 爽快思思 通用场景
# 中文
# zh_female_sinong_conversation_wvae_bigtts
# -
# 京腔侃爷 通用场景
# 中文
# zh_male_M392_conversation_wvae_bigtts

# 叠小态小姐BV700_V2_streaming 坍缩BV102_streaming 波函数先生BV107_streaming 费米子少女BV428_streaming
# 玻色子少女BV407_V2_streaming 希尔伯特大叔BV701_V2_streaming 量子比特御姐BV104_streaming


def check_csv():
	with open(Memory_wechat_path, 'r') as f:
		reader = csv.reader(f)
		current_data = list(reader)
		current_index = len(current_data)
		return current_data, current_index


def Memory_save(name, memory_entity, source=None, minutes=1):
	if str(memory_entity) == '{}':
		return "实体记忆为空，不需要存储。"
	else:
		# 读取CSV文件以获取当前的最大索引值
		current_data, current_index = check_csv()
		print(f"最大检索{current_index}")

		# 获取当前的日期和时间，包括秒
		save_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		# 检查是否存在相同的name和近期的time
		found = False
		for i, row in enumerate(current_data):
			if row[1] == name:
				time_diff = datetime.now() - datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
				if time_diff <= timedelta(minutes=minutes):
					# 如果存在，则覆盖memory_entity
					found = True
					k = i
					print("记忆已找到。")

		if not found:
			# 如果不存在，则添加新的数据行
			original_index_new = current_index + 2
			current_data.append([original_index_new, name, memory_entity, save_time, source])
			# 将数据写回CSV文件
			with open(Memory_wechat_path, 'w', newline='') as f:
				writer = csv.writer(f)
				writer.writerows(current_data)
			return "新记忆已保存。"
		else:
			current_data[k][2] = memory_entity
			with open(Memory_wechat_path, 'w', newline='') as f:
				writer = csv.writer(f)
				writer.writerows(current_data)
			return "记忆已更新。"


def memory_retrievals(name, source):
	# Read the CSV file to get the current maximum index value
	with open(Memory_wechat_path, 'r') as f:
		reader = csv.reader(f)
		current_data = list(reader)

	max_value = -1  # Initialize max_value to a very small number
	max_row = None  # Initialize max_row to None
	max_status = None  # Initialize max_status to None

	# Retrieve the memory_entity from the CSV file where row[0] is the largest and row[4] matches the source
	for row in current_data:
		if row[1] == name and row[4] == source and int(row[0]) > max_value:
			max_value = int(row[0])
			max_row = row
			if "已总结" not in max_row[2]:
				max_status = "未总结"
			else:
				max_status = "已总结"

	if max_row is not None:
		print(f"最新记忆：{max_row[2]}")
		return max_status, max_row[2]  # Return the memory_entity of the row with the largest value in the first column

	return "没有新记忆", None


#########################################interface_def#################################################################


def summarize_entity_memory(name, source="微信", threshold=4):
	Chat = Chat_memory()

	with open(Memory_wechat_path, 'r') as f:
		reader = csv.reader(f)
		current_data = list(reader)

	save_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	entity_count = 0
	entity_memory_sum = []
	rows_to_delete = []

	for i, row in enumerate(current_data):
		if row[1] == name and row[4] == source:
			entity_count += 1
			try:
				if isinstance(row[2], str):
					try:
						data = ast.literal_eval(row[2])
						if isinstance(data, dict):
							entity_memory_sum.append(data)
						else:
							entity_memory_sum.append({row[2]})
					except (SyntaxError, ValueError):
						entity_memory_sum.append({row[2]})
				elif isinstance(row[2], dict):
					entity_memory_sum.append(row[2])
				rows_to_delete.append(i)
			except SyntaxError:
				pass

	print(f"共有{entity_count}个记忆实体。")
	print(f"提取所有实体记忆: {entity_memory_sum}")

	if entity_count > threshold:
		# results = "\n".join([str(dict_) for dict_ in entity_memory_sum])
		print(f"开始总结——》提取实体记忆: {entity_memory_sum}")

		# Assuming Chat.memory_entity_chain.invoke({"input": str(results)}) is a valid method call
		Final_entity = Chat.memory_entity_chain.invoke({"input": str(entity_memory_sum)}).content
		text = Final_entity.replace('\n', ' ')
		print(f"记忆实体已总结，并删除未总结记忆: {Final_entity}")

		for index in sorted(rows_to_delete, reverse=True):
			del current_data[index]

		current_index = len(current_data) + 1
		print(f"current_index: {current_index}")
		current_data.append([current_index, name, text, save_time, source])

		with open(Memory_wechat_path, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerows(current_data)
		texts = Final_entity.replace('{', ' ')
		text = texts.replace('}', ' ')
		return text
	else:
		print("记忆实体未到总结数量。")
		result_None = "\n".join([str(dict_) for dict_ in entity_memory_sum])
		print(result_None)
		texts = result_None.replace('{', ' ')
		text = texts.replace('}', ' ')
		return str(text)


def write_csv(wechat_name, res):
	fields = ['name', 'taste', 'contact', 'location', 'buy_record']

	# 打开(或创建)一个名为output.csv的文件,使用写入模式
	with open('daily_tral/output.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
		# 创建一个csv writer对象，明确指定分隔符为逗号
		writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		# 如果文件是新创建的,写入字段名作为标题行
		if csvfile.tell() == 0:
			writer.writeheader()

		# 写入数据行
		writer.writerow({
			'name': wechat_name,
			'taste': res.taste,
			'contact': res.contact,
			'location': res.location,
			'buy_record': res.buy_record
		})

	print("数据已成功写入到output.csv文件中。")


###########################################################Chat模块################################################################

class Chat_memory:
	def __init__(self, function="you are helpfully assistant", max_history=18):
		self.wx = WeChat()
		self.chat_history = ChatMessageHistory()
		self.history_msg = deque(maxlen=max_history)
		self.llm_turbo = ChatOpenAI(api_key=config.OpenAI_API_KEY,
									base_url=config.OpenAI_API_BASE_URL, model="gpt-4-turbo",
									temperature=0.5)  # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo,gpt-4o

		self.llm_4o = ChatOpenAI(api_key=config.OpenAI_API_KEY,
								 base_url=config.OpenAI_API_BASE_URL, model="gpt-4o",
								 temperature=0.5)  # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo,gpt-4o

		self.llm_low = ChatOpenAI(api_key=config.OpenAI_API_KEY,
								  base_url=config.OpenAI_API_BASE_URL, model="gpt-4o",
								  temperature=0.3)  # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo,gpt-4o

		self.llm3 = ChatOpenAI(api_key=config.OpenAI_API_KEY,
							   base_url=config.OpenAI_API_BASE_URL, model="gpt-3.5-turbo-0125",
							   temperature=0.4)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

		self.llm3_low = ChatOpenAI(api_key=config.OpenAI_API_KEY,
								   base_url=config.OpenAI_API_BASE_URL, model="gpt-3.5-turbo-0125",
								   temperature=0.1)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

		self.llm_mini = ChatOpenAI(api_key=config.OpenAI_API_KEY,
								   base_url=config.OpenAI_API_BASE_URL, model="gpt-4o-mini",
								   temperature=0.7)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

		self.llm_mini_low = ChatOpenAI(api_key=config.OpenAI_API_KEY,
								   base_url=config.OpenAI_API_BASE_URL, model="gpt-4o-mini",
								   temperature=0.1)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

		self.llm_zhipu = ChatZhipuAI(temperature=0.6,
									 model="glm-4",  # glm-4,glm-3
									 zhipuai_api_key=config.ZhiPu_API_KEY, )

		self.llm_zhipu_new = ChatZhipuAI(temperature=0.6,
										 model="glm-4-0520",  # glm-4,glm-3
										 zhipuai_api_key=config.ZhiPu_API_KEY, )

		self.llm_zhipu_air = ChatZhipuAI(temperature=0.6,
										 model="glm-4-air",  # glm-4,glm-3
										 zhipuai_api_key=config.ZhiPu_API_KEY, )

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

		self.purpose_detect = ChatPromptTemplate.from_messages([
			("system",
			 f"你将要判断输入的回复的文字里是否有[]的目的"
			 f"主要看最新回复信息，也稍察历史记录,有就是Ture，否则就return False，只输出Ture或False。"),
			("user", "{input}")])

		self.purpose_doing = ChatPromptTemplate.from_messages([
			("system",
			 f"你扮演一个好朋友，你将要判断输入的回复的文字里是否有的目的像正常人一样聊天"
			 f"主要看最新回复信息，也稍察历史记录，然后有策略到引导对方达到你的目的，每次回复不超过30字，模拟真人微信聊天，直接输出聊天内容，不要输出其他的"),
			("user", "{input}")])

		self.Q_bake_star_word = PromptTemplate.from_template(
			f"你是QBA的客服助手，你将根据微信用户的名字和头像来推测用户喜好，目的是询问客户对Q产品的反馈"
			"[微信用户的名称是：{name}"
			"微信用户的签名是{signature}]"
			"不要刻意提及签名只用于推测喜好和，润物细无声的像朋友一样开场，借用它的一些元素,根据喜好设计一句开场白了，要激起人的好奇心，40个字以内："
		)

		self.star_word = ChatPromptTemplate.from_messages([
			("system",
			 f"你扮演一个好朋友，你将要判断输入的回复的文字里是否有的目的像正常人一样聊天"
			 f"根据user输入的目的，判断一个合理的开场语句，直接输出回复："),
			("user", "{input}")])

		self.Entity_summery = ChatPromptTemplate.from_messages([
			("system",
			 f"帮我总结一下记忆实体,把关键点人物（出现次数更多）和事件都进行总结，50个字以内放在summary_memory里，总结人物事件和关系，"
			 "输出格式比如'已总结'：'summary_memory'，只输出总结内容，不要输出其他的，不要\n"),
			("user", "{input}")])

		self.detect_prompt = PromptTemplate.from_template(
			f"你是语义分析机器人，根据user聊天记录回答判断AI是否得到相应的信息:"
			"AI搜集的信息：{task}"
			"costumer的聊天记录：{msg}"
			"如果询问的信息都能从user回复里得到（每一点都不能少）,而且要判断对话任务是否结束，如果是输出 Ture，否则就输出 False，通过分析来思考AI是否已经获得答案！"
			"let's think step by step! Finally get answer!")

		self.boolean_output = PromptTemplate.from_template(
			"根据这段话判断最终输出Ture还是False，不要输出其他的：{text}"
			"Ture or False："
		)



		self.summary_detect = PromptTemplate.from_template(
			"结论：【{text}】"
			"总结一下缺少哪些信息？,或者总结AI的核心建议，不要超过50个字！"
			"总结："
		)

		self.purpose_to_do_chain = self.purpose_doing | self.llm_zhipu
		self.purpose_chain = self.purpose_detect | self.llm_zhipu
		self.ask_chain = self.Ask_prompt | self.llm_mini
		self.chain = self.prompt | self.llm_turbo
		self.memory_chain = self.memory_prompt | self.llm_turbo
		self.start_chain = self.star_word | self.llm_mini
		self.memory_entity_chain = self.Entity_summery | self.llm_mini
		self.Q_bake_start = self.Q_bake_star_word | self.llm_zhipu_new
		self.detect_chain = self.detect_prompt | self.llm_mini
		self.boolean_chain = self.boolean_output | self.llm_mini
		self.summary_chain = self.summary_detect | self.llm_mini

	def save_history(self, who):
		# 创建以对方名称命名的文件夹
		# if not os.path.exists(f"/chat_history/{who}"):
		# 	os.makedirs(f"/chat_history/{who}")

		# 以时间戳命名文件
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"chat_history/{who}/{timestamp}.json"

		# 将聊天记录保存为 JSON 文件
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(list(self.history_msg), f, ensure_ascii=False, indent=4)

	def reset_history(self):
		self.history_msg = deque(maxlen=18)

	def get_user_messages(self, who):
		# 返回 history_msg 中所有 "user" 字段的内容
		return [msg[f"{who}"] for msg in self.history_msg if f"{who}" in msg]

	def detect_purpose(self, task, who):
		# res = self.detect_chain.invoke({"task": task, "msg": self.get_user_messages(who=who)})
		res = self.detect_chain.invoke({"task": task, "msg": self.history_msg})
		print("当前历史消息记录:")
		print(json.dumps(list(self.history_msg), ensure_ascii=False, indent=4))
		# 保存聊天记录
		print(res.content)
		return res.content

	def chat_by_purpose_ET_memory_retrieval(self, who, content, source="微信", signature=None):
		self.reset_history()
		self.wx.GetSessionList()  # 获取会话列表
		self.wx.ChatWith(who)  # 打开`who`的聊天窗口
		temp_msg = None
		stat, max_row = memory_retrievals(who, source)
		print(f"状态：{stat}，提取实体记忆:{max_row} ")
		if stat == "已总结":
			Entity = max_row
		elif stat == "没有新记忆":
			print(stat)
			Entity = None

		else:
			Entity = summarize_entity_memory(who, source=source)

		self.Echat = ConversationChain(
			llm=self.llm_4o,
			verbose=True,
			prompt=Wechat(var=content, entity=str(Entity)).Q_BAKE_TEMPLATE_END2END,
			memory=ConversationEntityMemory(llm=self.llm_mini_low)
		)
		K = 0
		ret = None
		# start_word = self.Q_bake_start.invoke({"name": who,"signature" : signature}).content
		start_word = f"{who},你上次抽到的霸王餐什么时候来吃"
		self.wx.SendMsg_hotkey(start_word, who)
		# 初始化存储消息的列表
		while True:
			try:
				friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][1]  # 获取朋友的名字和发送的信息
				if (friend_name == who) and (receive_msg != temp_msg):
					print(K)
					print(f'【{who}】发送：【{receive_msg}】')
					current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					self.history_msg.append({f"{who}": receive_msg,
											 "timestamp": current_timestamp})
					temp_msg = receive_msg
					if K >= 1:
						res = self.detect_purpose(task=content, who=who)
						boolean_res = self.boolean_chain.invoke({"text": res})
						if "True" in boolean_res:
							print(f"目的达成，退出聊天")
							# sleep_time = random.uniform(1, 10)
							# time.sleep(sleep_time)
							self.wx.SendMsg_hotkey("好的，我了解了，谢谢你的回复。拜拜", who)
							self.save_history(who)
							return self.get_user_messages(who=who), res
							break
						else:
							ret = self.summary_chain.invoke({"text": res})

					# Entity 模块
					if ret:
						reply_msg = self.Echat.predict(input=f"{receive_msg}\n*AI提醒：{ret.content}*")
					else:
						reply_msg = self.Echat.predict(input=receive_msg)

					pprint(f"回复内容【{reply_msg}】")
					# sleep_time = random.uniform(1, 10)
					# time.sleep(sleep_time)
					# print(f"等待时间{sleep_time}秒")
					self.wx.SendMsg_hotkey(reply_msg, who)
					current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					self.history_msg.append({"AI": reply_msg,
											 "timestamp": current_timestamp
											 })
					store_input = self.Echat.memory.entity_store.store
					pprint(f"记忆实体1：{store_input}")
					first_save = Memory_save(name=who, memory_entity=store_input, source=source)
					print(first_save)
					# 保存聊天记录
					print(receive_msg)
					K += 1
			except Exception as e:
				print(f"发生错误：{e}")


###############################################################chat###############################################################

def random_sleep(min=0, max=10):
	sleep_time = random.uniform(min, max)
	time.sleep(sleep_time)
	print(f"等待时间{sleep_time:.2f}秒")


def check_save_status(who, status, check=False):
    today_str = datetime.now().strftime("%Y-%m-%d")

    if check:
        with open('daily_tral/tral.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['name'] == who and row['date'].startswith(today_str):
                    if row['status'] == '已回复':
                        print(f"tral.{who}:已回复")
                        return True
                    print(f"tral.{who}:未回复")
                    return False
    else:
        fields = ['date', 'name', 'status', 'try']
        updated = False
        records = []

        # 读取现有的 CSV 文件内容
        try:
            with open('daily_tral/tral.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['name'] == who and row['date'].startswith(today_str):
                        row['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        row['status'] = status
                        row['try'] = int(row['try']) + 1
                        updated = True
                    records.append(row)
        except FileNotFoundError:
            # 如果文件不存在，继续执行，准备写入新文件
            pass

        # 如果没有找到今天同一个 name 的记录，则添加一条新记录
        if not updated:
            records.append({
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': who,
                'status': status,
                'try': 0
            })

        # 将所有记录写回文件
        with open('daily_tral/tral.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(records)

        print("状态log数据已成功写入到tral.csv文件中。")


class wechat_function(Chat_memory):
	def __init__(self, N=5, wait_time=timedelta(seconds=30)):
		super().__init__()
		self.K = 0
		self.N = N
		self.ret = None
		self.temp_msg = None
		self.start_word = None
		self.refection = self.detect_chain
		self.boolean = self.boolean_chain
		self.re_summary = self.summary_chain
		self.timeout = wait_time
		###############################################################prompt###############################################################

		self.detect_coupons = PromptTemplate.from_template(
			f"你是语义分析机器人，根据顾客都聊天记录回答判断AI是否正确发送coupons链接:"
			"coupons相关信息：{task}"
			"costumer的聊天记录：{msg}"
			"如果客户检查选择不参加或者已经确定参加，就只输出 Ture，"
			"如果客户在犹豫，还没有作出决定，或者链接还没有发送，就只输出 False，"
			"通过分析来思考AI是否正确作出引导，并给出建议！let's think step by step! Finally get answer!")
		self.summary_coupons = PromptTemplate.from_template(
			"结论：【{text}】"
			"总结有哪些建议和引导")

		###############################################################chain###############################################################

		self.detect_coupons_chain = self.detect_coupons | self.llm_mini
		self.summary_coupons_chain = self.summary_coupons | self.llm_mini

	###############################################################function###############################################################

	def my_detect_purpose(self, task, who):
		# res = self.detect_chain.invoke({"task": task, "msg": self.get_user_messages(who=who)})
		res = self.refection.invoke({"task": task, "msg": self.history_msg})
		print("当前历史消息记录:")
		print(json.dumps(list(self.history_msg), ensure_ascii=False, indent=4))
		# 保存聊天记录
		print(res.content)
		return res.content

	def summary_men(self, who, source="微信"):
		self.reset_history()
		self.wx.GetSessionList()  # 获取会话列表
		self.wx.ChatWith(who)  # 打开`who`的聊天窗口

		stat, max_row = memory_retrievals(who, source)
		print(f"状态：{stat}，提取实体记忆:{max_row} ")
		if stat == "已总结":
			Entity = max_row
			return Entity
		elif stat == "没有新记忆":
			print(stat)
			Entity = None
			return Entity

		else:
			Entity = summarize_entity_memory(who, source=source)
			return Entity

	def recheck_conversation(self, who, last_mag):
		self.reset_history()
		self.wx.GetSessionList()  # 获取会话列表
		self.wx.ChatWith(who)  # 打开`who`的聊天窗口

		self.temp_msg = last_mag
		friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][
			1]  # 获取朋友的名字和发送的信息
		if not (friend_name == who) and (receive_msg == self.temp_msg):
			print("检测后对方还未回复")
			check_save_status(who,"未回复",check=False)
			return False, None
		else:
			print("检测后对方已经回复")
			check_save_status(who, "未回复", check=False)
			return True, receive_msg
	
	def recheck_keyword(self, who, last_mag):
		self.reset_history()
		self.wx.GetSessionList()  # 获取会话列表
		self.wx.ChatWith(who)  # 打开`who`的聊天窗口

		self.temp_msg = last_mag
		friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][
			1]  # 获取朋友的名字和发送的信息
		if not (friend_name == who) and (self.temp_msg in receive_msg):
			print("检测后对方还未回复X")
			check_save_status(who,"未回复",check=False)
			return False, None
		else:
			print("检测后对方已经回复V")
			check_save_status(who, "未回复", check=False)
			return True, receive_msg

	def set_time_countdown(self, who):
		last_message_time = datetime.now()

		while True:
			current_time = datetime.now()  # 移到循环内部

			left_time = current_time - last_message_time
			print(f"{left_time.total_seconds():.2f}秒")
			print("------------------")
			print("进入首轮对话等待时间")
			print("------------------")
			print(f"循环时间：{current_time},共用时：{left_time.total_seconds():.2f}")
			print("------------------")
			friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][1]
			if (friend_name == who) and (receive_msg != self.start_word):
				print("收到消息")
				check_save_status(who=who,status="已回复",check=False)
				return True
			else:
				if current_time - last_message_time > self.timeout:
					print(f"超过{self.timeout.total_seconds():.2f}秒没有收到新回复，结束对话")
					return False
				else:
					# 可以添加一个小的延迟,避免CPU使用率过高
					time.sleep(0.2)

	def chat_send(self, who, receive_word):
		reply_msg = self.Echat.predict(input=receive_word)
		pprint(f"回复内容【{reply_msg}】")
		random_sleep(0, 10)
		# 随机等待时间回复
		self.wx.SendMsg_hotkey(reply_msg, who)
		current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.history_msg.append({"AI": reply_msg,
								 "timestamp": current_timestamp
								 })
		store_input = self.Echat.memory.entity_store.store
		pprint(f"记忆实体1：{store_input}")
		first_save = Memory_save(name=who, memory_entity=store_input, source="微信")
		print(first_save)
		# 保存聊天记录
		print(receive_word)
		self.K += 1



	###############################################################mian_chat###############################################################
	def start_chat(self, who, content, source="微信",interruption=False ,interruption_word=None):
		if interruption and interruption_word:
			print("叙话模式")
			self.chat_send(who, interruption_word)

		if self.set_time_countdown(who):
			while True:
				try:
					friend_name, receive_msg = self.wx.GetAllMessage[-1][0], self.wx.GetAllMessage[-1][
						1]  # 获取朋友的名字和发送的信息
					if (friend_name == who) and (receive_msg != self.temp_msg):
						print(self.K)
						print(f'【{who}】发送：【{receive_msg}】')
						current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
						self.history_msg.append({f"{who}": receive_msg,
												 "timestamp": current_timestamp})
						self.temp_msg = receive_msg
						if self.K >= self.N:
							res = self.my_detect_purpose(task=content, who=who)
							boolean = self.boolean_chain.invoke({"text": res}).content
							print(f"【最终输出: {boolean}】")
							if "True" in boolean:
								print(f"目的达成，退出聊天")
								random_sleep(0, 4)
								self.wx.SendMsg_hotkey("好的，我了解了，谢谢你的回复。拜拜", who)
								self.save_history(who)
								return self.get_user_messages(who=who), res
								break
							else:
								self.ret = self.re_summary.invoke({"text": res})

						# Entity 模块
						if self.ret:
							reply_msg = self.Echat.predict(input=f"{receive_msg}\n*AI提醒：{self.ret.content}*")
						else:
							reply_msg = self.Echat.predict(input=receive_msg)

						# self.chat_send(who, reply_msg)

						pprint(f"回复内容【{reply_msg}】")
						#random_sleep(0, 10)
						# 随机等待时间回复
						self.wx.SendMsg_hotkey(reply_msg, who)
						current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
						self.history_msg.append({"AI": reply_msg,
												 "timestamp": current_timestamp
												 })
						store_input = self.Echat.memory.entity_store.store
						pprint(f"记忆实体1：{store_input}")
						first_save = Memory_save(name=who, memory_entity=store_input, source=source)
						print(first_save)
						# 保存聊天记录
						print(receive_msg)
						self.K += 1
				except Exception as e:
					print(f"发生错误：{e}")
		else:
			check_save_status(who=who,status="未回复",check=False)
			print("超时已经记录在log里")
			return False, False




	##########################################################################################################################

	def new_member_collection(self, who, content, source="微信", signature=None, consumer_tag=""):
		# 新会员更新信息
		Entity = self.summary_men(who)
		Q = Q_bake(collection=content, tag=consumer_tag, entities=Entity)
		self.refection = self.detect_chain

		self.Echat = ConversationChain(
			llm=self.llm_zhipu_air,
			verbose=True,
			prompt=Q.Q_BAKE_NEW_MEMBER_PROMPT,
			memory=ConversationEntityMemory(llm=self.llm_mini_low)
		)



	def coupons_send(self, who, content, info="", signature=None, consumer_tag="", coupons_link=""):
		# 老会员拼团提醒

		Entity = self.summary_men(who)
		Q = Q_bake(collection=coupons_link, coupons_info=info, tag=consumer_tag, entities=Entity)
		self.refection = self.detect_coupons_chain
		self.re_summary = self.summary_coupons_chain

		self.Echat = ConversationChain(
			llm=self.llm_zhipu_air,
			verbose=True,
			prompt=Q.Q_BAKE_COUPONS,
			memory=ConversationEntityMemory(llm=self.llm_mini_low)
		)






############################################main#############################################################




if __name__ == "__main__":
	# wechat = wechat_function(N=2)
	# # wechat.restart(who="阿甘", last_mag="您好，阿甘先生，今天我们有香包贝果和牛油果贝果的团购活动，您有兴趣参加吗？")
	#
	# # main(wechat_name="阿甘", signature="你不善待我，我们就不必往来。")
	# main_coupons_send(wechat_name="阿甘", signature="你不善待我，我们就不必往来。", chat_turn=5)
	#check_save_status(who="阿甘",status="已回复", check=True)
	check_save_status("阿甘", "已回复", check=False)