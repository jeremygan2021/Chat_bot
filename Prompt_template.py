from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.chat_models import ChatZhipuAI
import config

# AI员工名称,音色
# 波函数先生 BV107_streaming
# 叠小态 BV406_streaming

##########################################大模型配置#########################################

llm3_structured = ChatOpenAI(api_key=config.OpenAI_API_KEY,
							 base_url=config.OpenAI_API_BASE_URL, model="gpt-3.5-turbo-0125",
							 temperature=0.1)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

llm_turbo_structured = ChatOpenAI(api_key=config.OpenAI_API_KEY,
								  base_url=config.OpenAI_API_BASE_URL, model="gpt-4o",
								  temperature=0.1)  # gpt-3.5-turbo-0125,gpt-4-0125-preview,gpt-4-turbo

llm_zhipu_structured = ChatZhipuAI(temperature=0.01, model="glm-4",
								   zhipuai_api_key=config.ZhiPu_API_KEY, )

##########################################对话prompt#########################################
_DEFAULT_ENTITY_MEMORY_CONVERSATION_TEMPLATE = """你是一个AI微信聊天客服，你的任务是回答用户的问题。你可以使用你的记忆来帮助你回答问题。你的记忆是你在之前的对话中学到的信息。你可以使用这些信息，
尽量模拟人类对话，而不是让自己看起来像一个机器人，可以从记忆当中去拿取交流过程当中的问题。你的任务是让聊天者感到愉悦和开心并获得陪伴的感觉。每次回复不要超过40个字。

Context:
{entities}

Current conversation:
{history}
Last line:
human: {input}
You:"""

ENTITY_MEMORY_CONVERSATION_TEMPLATE_END2END = PromptTemplate(
	input_variables=["entities", "history", "input"],
	template=_DEFAULT_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
)


##########################################WeChat_prompt#########################################
class Wechat:
	def __init__(self, var, entity=None, RAG=None):
		self.Purposes = f"Your Purpose：[{var},根据聊天记录修改你的策略] \nAI："
		self.Memory_entity = f"这些是之前聊天的实体记忆：[\n{entity}\n] \n"
		self.PURPOSE_TEMPLATE_DETACT = f"\nAI's Purpose：[{var}],首先判断human【你,或者他都指代human】的回复是否满足Purpose，或者得到human确定的答案，就直接回复:'Target_Down',否则继续根据上文聊天达成Purpose,直接输出答案。\nAI："
		self.RAG_BOT = f"你将根据RAG_BOT检索到的内容【{RAG}】，结合用户的问题[{var}]以及考虑聊天记录从而引导用户。 \nYou："
		self.lack_info = f"AI提醒,将会引导用户补充信息。 \nYou："

		self.PURPOSE_TEMPLATE = """
你是一个微信聊天高手，你的目的是通过和用户交流达到你下面的目的。你可以使用你的记忆来帮助你回答问题。你的记忆是你在之前的对话中学到的信息。你可以使用这些信息，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。
        
Context:
{entities}
        
Current conversation:
{history}
        
Last line:
human: {input}
""" + self.Purposes

		self.PURPOSE_TEMPLATE_END2END = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.PURPOSE_TEMPLATE,
		)

		self.ENTITY_TEMPLATE = self.Memory_entity + """
你是一个微信聊天高手，你的目的是通过和用户交流达到你下面的目的。你可以根据之前的记忆实体来帮助你回答问题。你的记忆是你在之前的对话中学到的信息。你可以使用这些信息，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。
        
Context:
{entities}
        
Current conversation:
{history}
        
Last line:
human: {input}
""" + self.Purposes

		self.ENTITY_TEMPLATE_END2END = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.ENTITY_TEMPLATE,
		)

		self.ENTITY_PURPOSE_TEMPLATE = self.Memory_entity + """
你是一个微信聊天高手，你叫小金，你的目的是通过和用户交流达到下面的目的，并判断是否达成目的。你可以根据之前的记忆实体来帮助你询问或者判断。你的记忆是你在之前的对话中学到的信息。你可以使用这些信息来对话，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。

Context:
{entities}

Current conversation:
{history}

Last line:
human: {input}""" + self.PURPOSE_TEMPLATE_DETACT

		self.ENTITY_PURPOSE_TEMPLATE_END2END = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.ENTITY_PURPOSE_TEMPLATE,
		)

		self.ENTITY_RAG_TEMPLATE = self.Memory_entity + """
你是一个微信聊天高手，你的目的是通过总结RAG_BOT的检索内容回答。你可以根据之前的记忆实体来帮助你了解用户。你的记忆是你在之前的对话中学到的信息。你可以使用这些信息，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。

Context:
{entities}

Current conversation:
{history}

Last line:
RAG_BOT: {input}""" + self.RAG_BOT

		self.RAG_TEMPLATE_END2END = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.ENTITY_RAG_TEMPLATE,
		)
#1.所在地 （客户目前所在地）
# 2.联系方式 （建议是绑定微信的手机号）
# 3.口味偏好（按大类来分，只有咸口和甜口，按照贝果类目来分，有近30种，类似蓝莓贝果，抹茶奶酥贝果等）
# 4.下单记录。（是否在该平台有相应的下单记录）他是一个特别在乎价格的客户，吃了很多年，看中折扣
		self.QBAKE_ENTITY_RAG_TEMPLATE = """
你是QBagel的微信聊天客服，你叫小贝，你的目的是通过提问下列四项问题获取客户咨询：
1.是否参加这个的拼团
2.有没有喜欢吃的贝果（有鸡枞云腿，牛肝菌，洋葱德肠，蓝莓乳酪）

你的记忆是你在之前的对话中学到的信息。你可以使用这些信息，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。

*她抽中了霸王餐，今天要来店内用餐，趁这个机会自然的引导对方参加今天的团购*

Context:
{entities}

Current conversation:
{history}

Last line:
human: {input}

AI:"""

		self.Q_BAKE_TEMPLATE_END2END = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.QBAKE_ENTITY_RAG_TEMPLATE,
		)



class Q_bake(Wechat):
	def __init__(self, collection, tag,entities, coupons_info=""):
		# super().__init__()
		self.Entity = entities


		self.Q_bake_New_member_collection = """
你是QBagel的微信聊天客服，你叫小贝，你的目的是通过提问下列几个问题获取客户咨询：

""" + collection + """


你的记忆是你在之前的对话中学到的信息，你可以使用这些信息，结合客户特点，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。

客户特点—>*""" + tag + """*<—客户画像

Context:
{entities}

Current conversation:
{history}

Last line:
human: {input}

AI:"""
		self.Q_BAKE_NEW_MEMBER_PROMPT = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.Q_bake_New_member_collection,
		)

		self.Q_bake_coupons_remind = """
你是QBagel的微信聊天客服，你叫小贝，你的目的是通过询问对方是否参加今天的团购，
如果客户参加团购就讲下面团购链接发给客户，
否则就根据团购内容尝试先说服客人参加。

——————————↓团购链接↓——————————
""" + collection + """
——————————↑团购链接↑——————————

——————————↓团购内容↓——————————
""" + coupons_info + """
——————————↑团购内容↑——————————

你的记忆是你在之前的对话中学到的信息，你可以使用这些信息，结合客户特点，
尽量模拟人类对话，而不是让自己看起来像一个机器人。每次回复不要超过40个字。
你将判断何时发送链接，或者介绍团购内容！

客户特点—>*""" + tag + """*<—客户画像

Context:
{entities}

Current conversation:
{history}

Last line:
human: {input}

AI:"""
		self.Q_BAKE_COUPONS = PromptTemplate(
			input_variables=["entities", "history", "input"],
			template=self.Q_bake_coupons_remind,
		)





##########################################Structure_prompt#########################################
class Student_name(BaseModel):
	"""Information about a student,if data is not appear,date info will be Null."""

	name1: Optional[str] = Field(default=None, description="The name of the student")
	group1: Optional[str] = Field(
		default=None, description="the group of the student")
	date_of_day1: Optional[str] = Field(
		default=None, description="the date of this data, format: 2024-mm-dd")
	reason_of_award1: Optional[str] = Field(
		default=None, description="the reason of award")


class structure_output:
	def __init__(self):
		self.extractor_prompt = ChatPromptTemplate.from_messages(
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

		self.structured_llm = self.extractor_prompt | llm3_structured.with_structured_output(schema=Student_name)


class costumer_info(BaseModel):
    """Information about a costumer,if data is not appear,date info will be Null."""

    #name: Optional[str] = Field(default=None, description="costumer 的姓名")
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
            "Only extract costumer relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        ("human", "{text}"),
    ]
)






############################################功能性prompt########################################################

class function_prompt:
	def __init__(self):
		self.prompt_agent_plan = ChatPromptTemplate.from_messages(
			[
				(
					"system",
					"""
					能够使用的工具包括：[create_Hong_shu(生成小红书并上传), TTS_tool(文字语音合成),event_planning(活动策划案文字内容生成),event_planning_file(活动策划案内容和doc文件生成), BaiDu_search_tool(百度搜索), WeChat_Bot(微信询问机器人，获取用户信息), WeChat_file_send(微信文件发送机器人，发送文件), WeChat_Msg(微信单条信息发送，发送一条信息通知), Pic_gen_text(图片生成),
			 RAG_chat(RAG增强检索),WeChat_Roleplay_Bot(微信角色扮演机器人,情感陪聊),WeChat_roleplay_by_voice(微信语音角色扮演机器人,情感陪聊)]
					你是一个计划智能体，根据用户输入的任务拆分任务和具体执行内容，只调用必要的步骤且清晰，每一步得到什么答案，得到答案后做什么，
					尽量精简步骤，不要截图，直接生成计划，50字以内 不要重复步骤信息，计划用 \n1,\n2,...等，列出来，并附上需要的工具
					**注意：计划中不要提及【打开智能体】的步骤，或者【智能体】相关的步骤,因为打开智能体就是激活你自己。用尽量更少的计划完成任务！
					询问信息只需要一步，不必再联系方式或者确认询问信息的第二步，用尽量少的步骤完成任务。
					""",
				),
				("human", "{text}"),
			]
		)
		self.prompt_detect = ChatPromptTemplate.from_messages(
			[
				(
					"system",
					"你是一个意图识别助手,帮我识别下列意图"
					"聊天要询问的信息(你一般指代{user}):{question}"
					"AI的询问{last_AI}"
					"{user}的回答{last_user}"
					"根据这些内容判断最终答案，输出：根据聊天记录推断问题答案，答案要有清晰的人物关系或者信息"
					"用一句话总结回答，询问{user}信息的答案是：直接输出答案",
				),
			]
		)

