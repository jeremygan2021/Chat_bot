import time
import os
import pyperclip
from DrissionPage import ChromiumPage
import tkinter.messagebox as mb
from web_function import WebImageDownloader
import pyautogui

class up_shu(WebImageDownloader):
    def __init__(self):
        super().__init__()
        self.web = "https://creator.xiaohongshu.com/login"
        self.picture_dir = os.path.join("WrokScript", "Upload_Agent", "Shu_pic")
        self.page = None

    def new_web(self):
        self.page = ChromiumPage()
        self.page.get(self.web)

    def run_login(self):

        if not self.page:
            self.new_web()

        self.page.ele('.css-wemwzq').click()
        time.sleep(2)
        src = self.get_src("css-1lhmg90")
        if src:
            if self.download_img_from_base64(src,file_name='HongShuqrcode'):

                print(f"登录二维码已下载到")




    def up_load(self,picture_path):
        drission = ChromiumPage()
        drission.get(self.web)
        # 输入对文本框输入账号
        time.sleep(2)
        # 定位到密码文本框并输入密码
        ele3 = drission.ele('text:发布笔记')
        time.sleep(1)
        ele3.click()
        time.sleep(1)
        ele4 = drission.ele('text:上传图文')
        ele4.click()
        ele6 = drission.ele('text:上传图片')
        ele6.click()
        # self.listen_click_muse(clickTimes=1, lOrR='left',
        #                        picture_path=r"D:\dev\WrokScript\Auto_titok\Shu_pic\picture_path.png", confH=0.86)
        time.sleep(2)
        pyperclip.copy(picture_path)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')

    def uplaod_info(self,title,context,location,open_web="私密",time_set=False,time_info=None):
        drission = ChromiumPage()
        time.sleep(1)
        ele1 = drission.ele('.el-input__inner')
        ele1.input(title)
        ele2 = drission.ele('#post-textarea')
        ele2.input(context)
        time.sleep(1)
        ele3 = drission.ele('.address-box')
        ele311 = ele3.ele('.el-input__inner')
        ele311.input(location)
        # ele31 = drission.ele('.el-input__wrapper')
        # ele31.click()
        ele41 = drission.ele('.el-radio-group')
        ele42 = drission.ele('text:私密')
        time.sleep(1)
        if open_web == "公开":
            ele41.click()
            print("公开")
        elif open_web == "私密":
            ele42.click()
            print("私密")
        time.sleep(1)
        if time_set is False:
            ele5 = drission.ele('text:立即发布')
            ele5.click()
            time.sleep(0.5)
        else:
            ele5 = drission.ele('text:定时发布')
            ele5.click()
            time.sleep(0.8)
            ele51 = drission.ele('.el-input__prefix')
            ele51.click()

            pyautogui.hotkey('ctrl', 'a')
            pyperclip.copy(time_info)
            pyautogui.hotkey('ctrl', 'v')


        if mb.askokcancel('确认发布', '是否检查确定发布小红书！'):
            ele6 = drission.ele('.^css-k3hpu2')
            ele6.click()
            mb.showinfo('发布状态', '已成功发布')
        else:
            print("text upload cancelled.")


    def up_load_video(self,video_path):
        drission = ChromiumPage()
        drission.get(self.web)
        # 输入对文本框输入账号
        time.sleep(2)
        # 定位到密码文本框并输入密码
        ele3 = drission.ele('text:发布笔记')
        time.sleep(1)
        ele3.click()
        time.sleep(1)
        eles = drission.ele('.upload-input')
        eles.click()
        # ele4 = eles.ele('text:上传视频')
        # ele4.click()

        # self.listen_click_muse(clickTimes=1, lOrR='left',
        #                        picture_path=r"D:\dev\WrokScript\Auto_titok\Shu_pic\picture_path.png", confH=0.86)
        time.sleep(2)
        pyperclip.copy(video_path)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')

    def up_load_video_info(self, picture_path,title,context,location,open_web="私密",time_set=False,time_info="2024-04-30 11:32"):
        page = ChromiumPage()
        page.ele(".c-input_inner").input(title)
        page.ele("#post-textarea").input(context)

        # if open_web == "私密":
        ele11 = page.ele(".formbox")
        ele12 = ele11.ele("@value=1")
        ele12.click()
        # page.ele("text:私密").click()
        if time_set is True:
            page.ele("text:定时发布").click()
            time.sleep(1)
            page.ele(".^css-1dbyz17").click()
            pyautogui.hotkey('ctrl', 'a')
            pyperclip.copy(time_info)
            pyautogui.hotkey('ctrl', 'v')
        page.ele(".single-input").input(location)

        #上传封面
        page.ele(".info").click()
        # ele.click()
        ele2 = page.ele('.^css-ckmc4o')
        ele2.ele("text:上传封面").click()
        ele3 = page.ele(".css-wzyxpg")
        ele3.ele(".wrapper").click()
        pyperclip.copy(picture_path)
        # 粘贴iexplore
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(2)
        ele4 = page.ele(".css-s2uf1z")
        ele4.ele(".^css-k3hpu2").click()

        if mb.askokcancel('确认发布', '是否检查确定发布小红书视频！'):
            ele6 = page.ele('.submit')
            ele6.ele("text:发布").click()

            mb.showinfo('发布状态', '已成功发布')
        else:
            print("Video upload cancelled.")




if __name__ == '__main__':
    UP = up_shu()
    UP.run_login()

    # UP.up_load(picture_path=r"D:\dev\WrokScript\Upload_Agent\Download_img\狗.jpg")
    # UP.uplaod_info("我是自动化AI",
    #                "牛逼不牛逼",
    #                "叠加态AI科技",
    #                False,
    #                True,
    #                "2024-04-27 18:42")


    #UP.up_load_video(video_path=r"C:\Users\PC\Downloads\Bro Downloads\vnc安装注册使用教程.mp4")
    # UP.up_load_video_info(
    #                       picture_path=r"E:\叠加态活动\AI\海报\坚持星球\BigJeremy_Seed_3184273313_A_light_blue_cyberpunk_city_Backgroun_5e7c17bf-c2c4-44ef-94c2-8f91651add05.png",
    #                       title="我是自动化AI",
    #                       context="牛逼不牛逼",
    #                       location="叠加态AI科技",
    #                       open_web="私密",
    #                       time_set=True)




