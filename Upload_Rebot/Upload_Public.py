import time
import pyautogui

import pyperclip
from DrissionPage import ChromiumPage
import tkinter.messagebox as mb

import os
import shutil

def rename_to_png(file_path):
    # 获取文件所在的目录和文件名
    directory, filename = os.path.split(file_path)

    # 创建新的文件名（添加.png后缀）
    new_filename = filename + '.png'

    # 构建新的完整文件路径
    new_file_path = os.path.join(directory, new_filename)
    try:
        # 重命名文件，如果文件已存在则覆盖
        shutil.move(file_path, new_file_path)
        print(f"文件已成功重命名为: {new_file_path}")

        # 删除原文件
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"原文件 {file_path} 已被删除")
        else:
            print(f"原文件 {file_path} 不存在，无需删除")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
    except PermissionError:
        print(f"错误: 没有权限操作文件 {file_path}")
    except Exception as e:
        print(f"操作文件时发生错误: {e}")



class Public_Upload:
    def __init__(self):
        self.page = ChromiumPage()
        self.web = "https://mp.weixin.qq.com/"
        self.web_up = "https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web"

    def login(self):
        # 打开目标网页
        self.page.get(self.web)  # 替换为实际的网页URL
        time.sleep(3)
        # 查找指定class的元素
        qrcode_elem = self.page.ele('.login__type__container__scan__qrcode')

        if qrcode_elem:
            # 获取图片的src属性
            img_src = qrcode_elem.attr('src')

            if img_src:
                # 设置保存路径和文件名
                save_dir = r'D:\AI_Machine_learning\CMbot\Upload_Rebot'
                file_name = 'qrcode'
                full_path = os.path.join(save_dir, file_name)
                # 下载图片
                self.page.download(img_src, full_path)
                file_path = r"D:\AI_Machine_learning\CMbot\Upload_Rebot\qrcode\scanloginqrcode"
                rename_to_png(file_path)
                if os.path.exists(full_path):
                    print(f"图片已下载并保存为: {full_path}")
                else:
                    print("图片下载失败")
            else:
                print("未找到图片src属性")
        else:
            print("未找到指定class的元素")

    def input_pic(self,picture):
        pyperclip.copy(picture)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.hotkey('enter')



    def Upload_article(self,title,author,content,subtitle,picture):
        self.page.get(self.web)
        ele1 = self.page.ele("text:图文消息")
        ele1.click()
        time.sleep(1)
        tab = self.page.latest_tab
        tab.ele("text:请在这里输入标题").input(title)
        tab.ele("#author").input(author)
        tab.ele(".view rich_media_content autoTypeSetting24psection").input(content)
        time.sleep(1)
        tab.scroll.to_bottom()
        tab_sub = tab.ele(".^frm_textarea")
        time.sleep(1)
        tab_sub.input(subtitle)
        tab.ele("text:拖拽或选择封面").hover()
        time.sleep(2)
        lists = tab.ele("#js_cover_null")
        # print(lists)
        time.sleep(1.5)
        lists.ele(".:js_imagedialog").click()

        pi_but = tab.ele(".^weui-desktop-global-mod")
        pi_but.ele(".:webuploader-pick").click()
        # pyautogui.hotkey('ctrl', 'a')
        time.sleep(1.5)
        self.input_pic(picture)
        time.sleep(6)
        downstream = tab.ele(".weui-desktop-dialog__ft")
        downstream.ele("text:下一步").click()
        downstream.ele("text:完成").click()
        sent = tab.ele(".^js_bot_bar")

        if mb.askokcancel("你是否要发布？","点击确定发布，点击取消保存为草稿"):
            sent.ele("#js_send").click()
            mb.showinfo('发布状态', '已成功发布')

        else:
            sent.ele("#js_submit").click()
            mb.showinfo('发布状态', '已保存为草稿')



if __name__ == '__main__':
    UP = Public_Upload()
    UP.Upload_article("今天的标题","阿甘","写的内容","subtitle","E:\叠加态活动\AI\海报\坚持星球\叠加态高级课.jpg")
    # UP.login()