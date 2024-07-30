import time
import pyautogui
# import PyOfficeRobot
import pyperclip
from DrissionPage import ChromiumPage
import tkinter.messagebox as mb
#自动化视频号上传

class Video_Upload:
    def __init__(self):
        self.page = ChromiumPage()
        self.web = "https://channels.weixin.qq.com/platform"
        self.web_up = "https://channels.weixin.qq.com/platform/post/create"

    def main_up(self, picture_path,subtitle,content,time_set=True):
        self.page.get(self.web)
        time.sleep(3)
        ele1 = self.page.ele(".post-list-header")
        ele1.ele("text:发表视频").click()
        self.page.ele(".input-editor").input(content)
        ele2 = self.page.ele(".post-short-title-wrap")
        ele2.ele(".weui-desktop-form__input").input(subtitle)
        if time_set is True:
            self.page.ele(".weui-desktop-form__check-label").click()

        #上传封面
        self.page.ele(".upload-content").click()
        pyperclip.copy(picture_path)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')

        if mb.askokcancel('确认发布', '是否检查确定发布微信视频号！'):
            ele6 = self.page.ele('.form-btns')
            ele6.ele("text:发表").click()
            mb.showinfo('发布状态', '已成功发布')
        else:
            print("Video upload cancelled.")





if __name__ == '__main__':
    v = Video_Upload()
    v.main_up(picture_path=r"D:\dev\WrokScript\Upload_Agent\text.png",
              content="人生都是我掌控不了的",
              subtitle="我知道你要的东西我给不了")