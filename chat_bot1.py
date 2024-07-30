from langchain_core.tools import tool
import csv
import os
import time
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from lib.langchain_chat_edit import langchain_chat
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
from datetime import datetime
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.runnables import (
	Runnable,
)

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
import config


class costumer_info(BaseModel):
	"""Information about a costumer,if data is not appear,date info will be Null."""

	# name: Optional[str] = Field(default=None, description="costumer 的姓名")
	taste: Optional[str] = Field(
		default=None, description="口味偏好，对贝果的洗好类型")
	contact: Optional[str] = Field(
		default=None, description="costumer 的联系方式，手机号之类的")
	location: Optional[str] = Field(
		default=None, description="costumer 的所在地")
	buy_record: Optional[str] = Field(
		default=None, description="costumer 的购买记录，是否之前有下单过")


extractor_prompt = ChatPromptTemplate.from_messages(
	[
		(
			"system",
			"You are an expert extraction algorithm. "
			"Only extract relevant information from the text. "
			"If you do not know the value of an attribute asked to extract, "
			"return null for the attribute's value.",
		),
		("human", "{text}"),
	]
)

prep_agent_prompt = ChatPromptTemplate.from_messages(
	[
		(
			"system",
			"你是QBagel的客服小助理，现在你将帮助QBagel的客户更好的了解他们的口味",
		),
		("human", "{text}"),
	]
)

chat = langchain_chat.Chat_memory(
	function="你将要判断输入的回复的文字里是否有喜欢贝果的'口味偏好'和'类型',要是没有就继续追问")

llm_turbo = ChatOpenAI(api_key=config.OpenAI_API_KEY,
					   base_url=config.OpenAI_API_BASE_URL, model="gpt-4-turbo",
					   temperature=0.5)  # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo,gpt-4o

llm_4o = ChatOpenAI(api_key=config.OpenAI_API_KEY,
					base_url=config.OpenAI_API_BASE_URL, model="gpt-4o",
					temperature=0.5)  # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo,gpt-4o

llm_low = ChatOpenAI(api_key=config.OpenAI_API_KEY,
					 base_url=config.OpenAI_API_BASE_URL, model="gpt-4o",
					 temperature=0.2)  # gpt-3.5-turbo-0125,gpt-4-0125-preview，gpt-4-turbo,gpt-4o

llm_mini = ChatOpenAI(api_key=config.OpenAI_API_KEY,
					  base_url=config.OpenAI_API_BASE_URL, model="gpt-4o-mini",
					  temperature=0.7)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

llm_mini_low = ChatOpenAI(api_key=config.OpenAI_API_KEY,
						  base_url=config.OpenAI_API_BASE_URL, model="gpt-4o-mini",
						  temperature=0.1)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

llm3 = ChatOpenAI(api_key=config.OpenAI_API_KEY,
				  base_url=config.OpenAI_API_BASE_URL, model="gpt-3.5-turbo-0125",
				  temperature=0.4)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

llm3_low = ChatOpenAI(api_key=config.OpenAI_API_KEY,
					  base_url=config.OpenAI_API_BASE_URL, model="gpt-3.5-turbo-0125",
					  temperature=0.1)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

llm_zhipu = ChatZhipuAI(temperature=0.6,
						model="glm-4",  # glm-4,glm-3
						zhipuai_api_key=config.ZhiPu_API_KEY, )

llm_zhipu_new = ChatZhipuAI(temperature=0.6,
							model="glm-4-0520",  # glm-4,glm-3
							zhipuai_api_key=config.ZhiPu_API_KEY, )

llm_zhipu_air = ChatZhipuAI(temperature=0.6,
							model="glm-4-air",  # glm-4,glm-3
							zhipuai_api_key=config.ZhiPu_API_KEY, )

chain = prep_agent_prompt | llm_zhipu

structured_llm = extractor_prompt | llm_mini_low.with_structured_output(schema=costumer_info)


#######################################  tools  ############################################
@tool
def create_CSV_file(today: str, n):
	"如果没有get_CSV_file返回None，N取决于有多少个用户,就创建一个根据日期创建的CSV文件,如果存在路径就不使用这个函数，用于记录消费者们的信息,如果没有日期，就默认使用当天的日期,格式为<yyyy-mm-dd>"
	# 指定 CSV 文件的名称

	filename = f'\\{today}.csv'

	# 打开文件，准备写入
	with open(filename, mode='w', newline='') as file:
		writer = csv.writer(file)

		# 写入标题行
		writer.writerow(['日期', '姓名', '口味偏好', '联系方式', "所在地", '下单记录'])

		for i in range(n):
			writer.writerow([today, "无", '无', '无', '无', '无'])

	message = f"CSV文件{filename}创建成功！"
	print(message)
	return message


@tool
def edit_our_user(date: str, name: str, contact: int, taste: str, location: str, buy_record: str):
	"""如果存在date文件，就把客户的相关信息放入加入到CSV格式当中，"""
	file_path = f'\\{date}.csv'

	# 读取原始数据
	with open(file_path, mode='r', newline='') as file:
		reader = csv.reader(file)
		data = list(reader)

	# 检查组号并加入学生姓名及获奖原因
	if len(data) == name:  # 确保该组存在
		data = [date, name, contact, taste, location, buy_record]  # 加入获奖原因

	# 将修改后的数据写回文件
	with open(file_path, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(data)

	message = f"{name},{contact},{taste},{location},{buy_record}信息写入成功！"
	print(message)
	return message


@tool
def get_tody_date():
	"要是日期是None,就默认使用当天的日期,格式为<yyyy-mm-dd>"
	today = datetime.today().strftime('%Y-%m-%d')
	print(f"今天日期是：{today}")
	return today


@tool
def get_CSV_file(today: str):
	"获取指定日期的CSV文件,用今天的日期寻找CSV,格式 YYYY-MM-DD,如果没有就返回None，有的话就返回文件路径"
	file_path = f'\\{today}.csv'
	if os.path.exists(file_path):
		print(f"找到了{today}的文件")
		return file_path
	else:
		print(f"没有找到{today}的文件")
		return None


@tool
def detect_null_name(date: str):
	"检测CSV文件中哪些组的获奖学员名称为‘无’，并返回这些组的组名。"
	file_path = f'\\{date}.csv'

	with open(file_path, mode='r', newline='', encoding='gbk') as file:
		reader = csv.reader(file)
		next(reader)  # 跳过表头
		null_groups = []
		for row in reader:
			if row[2] == '无':
				null_groups.append(row[1])  # 收集组名
	print(f"在 {date} 的CSV文件中，以下组的获奖学员名称为‘无’：{null_groups}")

	return null_groups


@tool
def detect_student_group_and_name(date: str):
	"""
	检测CSV文件中的学员组别和姓名，返回包含所有有效组名及其对应获奖学员姓名的列表。
	确保排除姓名为‘无’及组名为‘无小组’的记录。
	"""
	file_path = f'\\{date}.csv'
	valid_results = []  # 用于存储排除无效记录后的组名及对应的获奖学员姓名

	with open(file_path, mode='r', newline='', encoding='gbk') as file:
		reader = csv.reader(file)
		next(reader)  # 跳过表头
		for row in reader:
			group_name = row[1]
			student_name = row[2]
			# 确保姓名不为'无'且组名不为'无小组'才加入结果
			if student_name != '无' and student_name != '无小组':
				valid_results.append((group_name, student_name))

	print(f"在 {date} 的CSV文件中，排除无效记录后，有效学员组别及姓名信息如下：")
	for group, name in valid_results:
		print(f"组名：{group}, 姓名：{name}")

	return valid_results


@tool
def AI_Agent_for_chat(who, null_group):
	"通过invok_work_agent->微信agent去询问会员的反馈信息，who是会员微信名称"


#######################################  tools  ############################################

def new_agent(task):
	memory = SqliteSaver.from_conn_string(":memory:")

	new_tools = [create_CSV_file, get_tody_date]
	agent_executor = create_react_agent(llm_zhipu, new_tools, checkpointer=memory)

	# Use the agent
	config = {"configurable": {"thread_id": "abc123"}}
	for chunk in agent_executor.stream(
			{"messages": [HumanMessage(content=task)]}, config
	):
		print(chunk)
		print("----")


if __name__ == '__main__':
	new_agent("帮我检查今天的csv，如果没有就创建")
	# res = chain.invoke({"text":"你是谁"})
