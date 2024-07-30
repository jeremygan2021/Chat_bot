from WeChat_Bot import wechat_function, write_csv, check_save_status, current_dir
from chat_bot1 import structured_llm
import csv
from lib.PyOfficeRobot.api import chat, file
from collections import Counter
from datetime import date
import os

from datetime import datetime, timedelta

class stat:
	def for_csv(self, file_path=r'D:\AI_Machine_learning\CMbot\friends_lists.csv'):

		with open(file_path, mode='r', encoding='utf-8') as file:
			csv_reader = csv.DictReader(file)
			for row in csv_reader:
				if row['RemarkName']:
					print(row['RemarkName'])

	def for_search_csv(self, file_path=r'D:\AI_Machine_learning\CMbot\friends_lists.csv'):
		with open(file_path, mode='r', encoding='utf-8') as file:
			csv_reader = csv.DictReader(file)
			remark_counter = Counter()

			for row in csv_reader:
				if "老" in row['RemarkName']:
					print(row['RemarkName'])
					remark_counter.update(['matches'])

		print(f"搜索结果一共有: {remark_counter['matches']}")


################################################################################

def new_member_data_coll(who, ret2):
	print(ret2)
	res = structured_llm.invoke(input=ret2)
	print(res)
	write_csv(who, res)
	return True


def coupons_data_coll():
	pass


def main_new_member(wechat_name,
					demend,
					signature=None,
					chat_turn=5):
	path = os.path.abspath(os.path.join(current_dir, 'chat_history'))

	if not os.path.exists(f"{path}/{wechat_name}"):
		print("创建用户历史文件夹")
		os.makedirs(f"{path}/{wechat_name}/")

	wechat = wechat_function(N=chat_turn)
	wechat.new_member_collection(who=wechat_name,
											 content=demend,
											 signature=signature)

	# start_word = self.Q_bake_start.invoke({"name": who,"signature" : signature}).content
	start_word = f"""哈喽{wechat_name}同学,你好！
	
	我是QBagel官方运营 小贝，感谢您曾经的光顾支持。"""

	chat.send_message_hotkey(wechat_name, start_word)
	#wechat.wx.SendMsg_hotkey(wechat.start_word, demend)
	# 初始化存储消息的列表
	his, ret2 = wechat.start_chat(wechat_name, demend)  # 开始

	return new_member_data_coll(wechat_name, ret2)


def main_coupons_send(wechat_name,
					  demend="询问对方1.是否参加拼团。",
					  signature=None,
					  consumer_tag="阿甘是一个非常自以为是但是喜欢咖啡的老客户",
					  coupons_link="coupons link: www.tangledup-ai.com",
					  info="今天的团购内容是香包贝果和牛油果贝果3人拼团半价",
					  chat_turn=5,
					  wait_time=timedelta(seconds=15)):
	print(f"每轮等待时间:{wait_time}")
	path = os.path.abspath(os.path.join(current_dir, 'chat_history'))

	if not os.path.exists(f"{path}/{wechat_name}"):
		print("创建用户历史文件夹")
		os.makedirs(f"{path}/{wechat_name}/")

	wechat = wechat_function(N=chat_turn, wait_time=wait_time)
	wechat.coupons_send(who=wechat_name,
						content=demend,
						info=info,
						coupons_link=coupons_link,
						signature=signature,
						consumer_tag=consumer_tag)
	# start_word = self.Q_bake_start.invoke({"name": who,"signature" : signature}).content
	#file.send_file_new(who=wechat_name,file='D:/CMbot/picture.jpg')
	start_word = f"""哈喽{wechat_name}同学,你好！\n我是QBagel官方运营 小贝，为答谢老客户的支持，我们今天有一个拼团活动，你有没有兴趣。\n每件贝果在正价基础上直降3—7元，限量25份"""
	chat.send_message_hotkey(wechat_name, start_word)
	# 初始化存储消息的列表
	wechat.N = 2
	ret, ret2 = wechat.start_chat(wechat_name, demend)  # 开始

	if ret:
		print("结束")
		return True
	else:
		print("超时")
		return False

def recheck_new_member(chat_trun=5, target=''):
	wechat = wechat_function(N=chat_trun)
	with open('daily_tral/new_member.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			who = row['name']
			print(f"进入【{who}】的未回复检测循环")
			if check_save_status(who=who, status="未回复", check=True):
				print(f'{who}未回复')
				continue

			last_msg = f"哈喽{who}"
			res, msg = wechat.recheck_keyword(who=who, last_mag=last_msg)
			print(f"{who}的最后一条信息接收到：{msg}")
			if res:
				print(f"开始重新新会员信息收集{who}")
				wechat.temp_msg = None
				wechat.new_member_collection(who=who,
											 content=target,
											 consumer_tag=row['consumer_tag'])
				wechat.N = 3
				res, ret = wechat.start_chat(who=who, content=target, interruption=True, interruption_word=msg)

				if ret:
					print("结束")
				else:
					print("超时")
			else:
				print('还没回复')

	print("循环结束")



def recheck_coupons_main(chat_trun=5):
	wechat = wechat_function(N=chat_trun)

	with open('daily_tral/run.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			who = row['name']
			print(f"进入【{who}】的未回复检测循环")
			if check_save_status(who=who, status="未回复", check=True):
				print(f'{who}未回复')
				continue

			last_msg = f"哈喽{who}"
			res, msg = wechat.recheck_keyword(who=who, last_mag=last_msg)
			print(f"{who}的最后一条信息接收到：{msg}")
			if res:
				print(f"开始重新对话{who}")
				wechat.temp_msg = None
				wechat.coupons_send(who=who,
									content=row['target'],
									info=row['info'],
									coupons_link=row['coupons_link'],
									consumer_tag=row['consumer_tag'])
				wechat.N = 3
				res, ret = wechat.start_chat(who=who, content=row['target'], interruption=True, interruption_word=msg)

				if ret:
					print("对话结束")
				else:
					print("对话超时")
			else:
				print(f'{who}还没回复')

	print("所有用户处理完成")

def main_send_order():
    today = date.today().strftime("%Y/%m/%d")
    updated_rows = []
    send = 0

    with open('daily_tral/order.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        for row in reader:
            who = row['name']
            order_date = row['date']
            order_info = row['order_info']
            order_id = row['order_id']
            status = row['status']
            print("------------------")
            print(who, order_date, order_info, order_id, status)
            print("------------------")

            if order_date == today and status.lower() == 'off':
                print("--------任务启动--------")
                print(f"给【{who}】发送订单信息")
                msg = f"订单{order_id}已发货，以下是具体订单信息\n{order_info}，请及时查收。"
                print(msg)
                print("------------------")
                chat.send_message_hotkey(who, msg)
                row['status'] = 'on'
                send += 1

            updated_rows.append(row)

    # Write the updated data back to the CSV file
    with open('daily_tral/order.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    print(f"发送完毕，一共发送{send}条订单信息")


def main_collection():
	updated_rows = []

	with open('daily_tral/new_member.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		fieldnames = reader.fieldnames

		for row in reader:
			if row['status'].lower() == 'off':
				who = row['name']
				if main_new_member(who, "询问对方1.目前的居住地（城市）,2.喜欢的贝果口味偏好,3.电话号码, 4.邀请加入我们的粉丝微信群【贝GIRL生活圈】好处【超多精品社群活动，大咖分享还可周周领社群专属贝果券，参与超级秒杀，福利团购，吃霸王餐喔💰】。",
								   row['consumer_tag']):
					print(f"{who}第一轮收集成功")
					row['status'] = 'on'
				else:
					print(f"{who}第一轮收集超时")

				updated_rows.append(row)

	# Write the updated data back to the CSV file
	with open('daily_tral/new_member.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(updated_rows)

def loop_for_new_member(nub=3):
	print(f"计划执行{nub}轮收集")
	for i in range(nub):
		print(f"开始第{i + 1}轮收集")
		recheck_new_member(
			target='询问对方1.目前的居住地（城市）,2.喜欢的贝果口味偏好,3.电话号码, 4.邀请加入我们的粉丝微信群【贝GIRL生活圈】好处【超多精品社群活动，大咖分享还可周周领社群专属贝果券，参与超级秒杀，福利团购，吃霸王餐喔💰】。')
	print("所有轮次收集完成")


def loop_for_coupons(nub=3):
	print(f"计划执行{nub}轮收集")
	for i in range(nub):
		print(f"开始第{i + 1}轮收集")
		recheck_coupons_main()
	print("所有轮次收集完成")

def main_coupons():
	with open('daily_tral/run.csv', 'r', newline='', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			who = row['name']
			if main_coupons_send(who, row['target'], info=row['info'], coupons_link=row['coupons_link'], consumer_tag=row['consumer_tag']):
				print(f"{who}第一轮激活成功")
			else:
				print(f"{who}第一轮超时")



if __name__ == '__main__':
	# main()
	main_new_member("阿甘")

