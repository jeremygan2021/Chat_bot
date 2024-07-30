from DrissionPage import ChromiumPage
import os
from pathlib import Path
import base64

class WebImageDownloader:
    def __init__(self, save_dir='D:/dev/CMbot/Upload_Rebot'):
        self.page = ChromiumPage()
        self.save_dir = Path(save_dir)

    def get_src(self,class_tag):
        img = self.page.ele(f'.{class_tag}')
        if not img:
            print(f"未找到指定class '{class_tag}' 的元素")
            return None

        img_src = img.attr('src')
        if not img_src:
            print("未找到图片src属性")
            return None
        return img_src

    def download_img(self, class_tag, file_name='qrcode'):
        img = self.page.ele(f'.{class_tag}')
        if not img:
            print(f"未找到指定class '{class_tag}' 的元素")
            return None

        img_src = img.attr('src')
        if not img_src:
            print("未找到图片src属性")
            return None

        try:
            self.page.download(img_src, file_name)
            self.rename_to_png(f"/qrcode/{file_name}")
            print(f"图片已下载并保存为:/qrcode/{file_name}")
            return f"/qrcode/{file_name}"
        except Exception as e:
            print(f"图片下载失败: {e}")
            return None

    def download_img_from_base64(self, base64_str, file_name='qrcode'):
        if not base64_str.startswith('data:image'):
            print("无效的base64字符串")
            return None

        # 提取base64数据
        base64_data = base64_str.split(',')[1]
        full_path = self.save_dir / f"xiaohongshu_qr/{file_name}.png"

        try:
            # 解码并保存为图像文件
            with open(full_path, 'wb') as file:
                file.write(base64.b64decode(base64_data))
            print(f"图片已下载并保存为: {full_path}")
            return full_path
        except Exception as e:
            print(f"图片下载失败: {e}")
            return None

    @staticmethod
    def rename_to_png(file_path):
        path = Path(file_path)
        new_path = path.with_suffix('.png')
        if path.exists():
            path.rename(new_path)
        return new_path

# 使用示例
if __name__ == "__main__":
    downloader = WebImageDownloader()
    result = downloader.download_img('scanloginqrcode', 'qr_code')
    if result:
        print(f"下载成功，文件保存在: {result}")
    else:
        print("下载失败")