import time
import pyautogui
# import PyOfficeRobot
import pyperclip
from DrissionPage import ChromiumPage
import tkinter.messagebox as mb
from tkinter import filedialog

class Titok_Upload:
    def __init__(self):
        self.page = ChromiumPage()
        self.web = "https://www.douyin.com/user/self"
        self.web_up = "https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web"

    def Login(self,video_path):
        dir = ChromiumPage()
        dir.get(self.web)
        time.sleep(8)
        # 点击上传按钮


    def UpLoad_Pic(self,front_pic):
        dir = ChromiumPage()

        ele5 = dir.ele("text:选择封面")
        ele5.click()
        time.sleep(5)
        ele6 = dir.ele("text:上传封面")
        ele6.click()
        ele7 = dir.ele(".content--1cIdN")
        ele7.click()
        pyperclip.copy(front_pic)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(2)
        ele0 = dir.ele(".uploadCrop--sZYxF")
        ele0.ele(".:finish--3_3_P").click()

    def Upload_laction(self,location):
        dir = ChromiumPage()
        ele5 = dir.ele("text:输入地理位置")
        ele5.click()
        pyperclip.copy(location)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(3.5)
        ele6 = dir.ele(".^semi-select-option")
        ele6.click()

    def UpLoad(self,
               video_path,
               title,
               content,
               front_pic=None,
               location=None,
               public=None,
               time_info=None):

        dir = ChromiumPage()
        dir.get(self.web_up)
        time.sleep(5)
        # # 点击上传按钮
        # ele1 = dir.ele(".xhLouUc0")
        # ele1.click()
        ele2 = dir.ele("text:为了更好的观看体验和平台安全，平台将对上传的视频预审。超过40秒的视频建议上传横版视频")
        ele2.click()
        time.sleep(1)
        pyperclip.copy(video_path)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(5)
        ele3 = dir.ele(".^semi-input")
        ele3.input(title)
        ele4 = dir.ele(".^zone-container")
        ele4.input(content)
        time.sleep(3)

        if front_pic is not None:
            # front_pic = filedialog.askopenfilename()
            # mb.showinfo('上传已有封面', '选择封面')
            self.UpLoad_Pic(front_pic)

        if location is not None:
            time.sleep(3)
            self.Upload_laction(location)
        if public == "好友":
            ele5 = dir.ele("text:好友可见")
            ele5.click()
        elif public == "私密":
            ele5 = dir.ele("text:仅自己可见")
            ele5.click()
        else:
            pass

        if time_info is not None:
            ele6 = dir.ele("text:定时发布")
            ele6.click()
            ele61 = dir.ele(".semi-datepicker-input")
            ele61.click()
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'a')
            pyperclip.copy(time_info)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)
        # mb.showinfo('确认发布', '等待上传完毕再点击确定！')
        if mb.askokcancel('确认发布', '等待上传完毕再点击确定！'):
            finals = dir.ele(".content-confirm-container--anYOC")
            final = finals.ele("text:发布")
            final.click()
            mb.showinfo('上传成功', '视频上传成功')
        else:
            print("Video upload cancelled.")






if __name__ == '__main__':
    Tk = Titok_Upload()
    Tk.UpLoad(r"E:\叠加态活动\AI\海报\坚持星球\WeChat_20230424105951.mp4",
              "hhhh",
              "AI自动生成",
              None,
              "叠加态AI",
              "私密")
