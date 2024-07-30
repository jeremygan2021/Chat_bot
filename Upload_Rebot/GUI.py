import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import time
import threading
import os
import ttkbootstrap as tb

# 视频上传应用程序类
class VideoUploaderApp:
    def __init__(self, root):
        """
        初始化视频上传应用程序
        :param root: 主窗口对象
        """
        self.root = root
        self.root.title("视频上传器")
        self.root.geometry("800x450")

        # 使用ttkbootstrap主题
        self.style = tb.Style(theme="darkly")

        # 设置字体
        self.font = ('Helvetica', 12)

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建右侧按钮框架
        self.side_frame = ttk.LabelFrame(root, text="平台选择", padding="10", style='primary.TLabelframe')
        self.side_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # 初始化界面组件
        self.init_widgets()

    def init_widgets(self):
        """
        初始化界面组件
        """
        # 创建上传按钮
        self.upload_button = ttk.Button(self.main_frame, text="上传视频", command=self.upload_video, style='info.TButton')
        self.upload_button.pack(pady=10)

        # 创建二维码标签
        self.qr_code_label = ttk.Label(self.main_frame)
        self.qr_code_label.pack(pady=10)

        # 创建上传进度标签
        self.progress_label = ttk.Label(self.main_frame, text="上传进度: 0%", font=self.font)
        self.progress_label.pack(pady=10)

        # 创建进度条
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=400, mode="determinate", style='success.Horizontal.TProgressbar')
        self.progress_bar.pack(pady=10)

        # 创建完成扫描按钮
        self.finish_scand_button = ttk.Button(self.main_frame, text="完成扫描", command=self.finish_scand, style='success.TButton')
        self.finish_scand_button.pack(pady=10)

        # 创建视频信息标签框架
        self.info_frame = ttk.LabelFrame(self.main_frame, text="视频信息", padding="10", style='primary.TLabelframe')
        self.info_frame.pack(pady=10, padx=10, fill=tk.X)

        # 创建视频信息标签
        self.video_info_label = ttk.Label(self.info_frame, text="未上传", font=self.font, foreground="white", background="black", padding=10, relief="solid", anchor='center')
        self.video_info_label.pack(pady=10, padx=10, fill=tk.X)

        # 创建右侧按钮
        self.create_side_buttons()

        # 加载并显示二维码
        self.load_qr_code()

    def upload_video(self):
        """
        选择并上传视频文件
        """
        file_path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4;*.avi;*.mov")])
        if file_path:
            self.update_progress(0)
            # 这里可以添加上传视频的逻辑
            self.update_progress(100)
            video_name = os.path.basename(file_path)
            video_format = os.path.splitext(file_path)[1]
            video_size = os.path.getsize(file_path) / (1024 * 1024)  # 以MB为单位
            self.video_info_label.config(text=f"视频名称: {video_name}\n格式: {video_format}\n大小: {video_size:.2f} MB")
            messagebox.showinfo("上传完成", "视频已成功上传!")

    def update_progress(self, percentage):
        """
        更新上传进度
        :param percentage: 上传进度百分比
        """
        self.progress_label.config(text=f"上传进度: {percentage}%")
        self.progress_bar['value'] = percentage

    def load_qr_code(self, qr_code_path=None):
        """
        加载并显示二维码
        :param qr_code_path: 二维码文件路径
        """
        if qr_code_path is None:
            qr_code_path = r'D:\dev\CMbot\Upload_Rebot\qrcode\scanloginqrcode.png'
        img = Image.open(qr_code_path)

        # 缩小二维码图像
        new_size = (150, 150)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        img_tk = ImageTk.PhotoImage(img)

        # 显示二维码
        self.qr_code_label.config(image=img_tk)
        self.qr_code_label.image = img_tk

    def finish_scand(self):
        """
        完成扫描操作，隐藏二维码并显示上传进度
        """
        # 隐藏二维码
        self.qr_code_label.config(image=None)

        # 显示进度条并设置为0%
        self.progress_bar.pack(pady=10)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="上传进度: 0%")

        # 启动一个线程模拟网络进度更新
        threading.Thread(target=self.simulate_progress).start()

    def simulate_progress(self):
        """
        模拟上传进度更新
        """
        for i in range(101):
            time.sleep(0.05)
            self.update_progress(i)

    def create_side_buttons(self):
        """
        创建平台选择按钮
        """
        # 创建按钮
        button_texts = ["抖音", "小红书", "视频号"]
        button_paths = {
            "抖音": r'D:\dev\CMbot\Upload_Rebot\douying\douyingqrcode.png',
            "小红书": r'D:\dev\CMbot\Upload_Rebot\xiaohongshu_qr\HongShuqrcode.png',
            "视频号": r'D:\dev\CMbot\Upload_Rebot\qrcode\scanloginqrcode.png'
        }
        for text in button_texts:
            button = ttk.Button(self.side_frame, text=text, command=lambda t=text: self.handle_side_button_click(t, button_paths[t]), style='primary.TButton')
            button.pack(pady=10, padx=10)

    def handle_side_button_click(self, platform, qr_code_path):
        """
        处理平台选择按钮点击事件
        :param platform: 平台名称
        :param qr_code_path: 平台对应的二维码文件路径
        """
        self.load_qr_code(qr_code_path)
        messagebox.showinfo("按钮点击", f"点击了 {platform} 按钮")

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = VideoUploaderApp(root)
    root.mainloop()
