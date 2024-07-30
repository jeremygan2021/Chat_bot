import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import ttkbootstrap as ttkb
import main_code
from data_update import data
import pandas as pd
import os


class CSVViewer:
    def __init__(self, root):
        self.root = root
        self.root.title('【Q贝果】机器人数据展示')
        self.root.geometry('800x600')

        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_buttons()
        self.create_treeview()

    def create_buttons(self):
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=10)

        options = [
            ('今日拼团数据', r'\daily_tral\run.csv'),
            ('今日订单发送数据', r'\daily_tral\order.csv'),
            ('聊天未回复情况', r'\daily_tral\tral.csv'),
            ('新人询问名单', r'\daily_tral\new_member.csv'),
            ('新人询问数据', r'\daily_tral\output.csv'),
        ]

        for text, file_path in options:
            ttk.Button(button_frame, text=text, command=lambda p=file_path: self.load_csv(p)).pack(side=tk.LEFT, padx=5)

    def create_treeview(self):
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.treeview = ttk.Treeview(tree_frame)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.treeview.xview)
        h_scrollbar.pack(fill=tk.X)
        self.treeview.configure(xscrollcommand=h_scrollbar.set)

    def load_csv(self, file_path):
        # 清除现有的treeview数据
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        try:
            # 获取当前脚本的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建完整的文件路径
            full_path = os.path.join(current_dir, file_path.lstrip('\\'))

            # 读取CSV文件
            df = pd.read_csv(full_path)

            # 在treeview中插入数据
            self.treeview["columns"] = list(df.columns)
            self.treeview.column("#0", width=0, stretch=tk.NO)

            # 自动调整列宽
            for col in self.treeview["columns"]:
                self.treeview.column(col, anchor=tk.CENTER, width=tk.font.Font().measure(col))
                self.treeview.heading(col, text=col)

            # 插入数据行并更新列宽
            for index, row in df.iterrows():
                self.treeview.insert(parent='', index='end', iid=index, text='', values=tuple(row))
                for i, value in enumerate(row):
                    col_width = tk.font.Font().measure(str(value))
                    if self.treeview.column(self.treeview["columns"][i], width=None) < col_width:
                        self.treeview.column(self.treeview["columns"][i], width=col_width)

        except FileNotFoundError:
            print(f"Error: CSV file not found at {full_path}")
        except pd.errors.EmptyDataError:
            print(f"Error: The CSV file at {full_path} is empty.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

def show_data():
    root = tk.Tk()
    data_app = CSVViewer(root)
    root.mainloop()

class AdaptiveGUI(ttkb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("【Q贝果】自动化机器人")
        self.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建并配置网格
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 更新数据按钮（带下拉菜单）
        update_data_frame = ttk.Frame(main_frame)
        update_data_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        update_data_button = ttk.Menubutton(update_data_frame, text="更新数据", style="primary.TMenubutton")
        update_data_button.pack(fill=tk.X, expand=True)

        update_menu = tk.Menu(update_data_button, tearoff=0)
        update_menu.add_command(label="更新拼团数据", command=self.update_group_buy_data)
        update_menu.add_command(label="更新订单数据", command=self.update_order_data)
        update_menu.add_command(label="更新邀请数据", command=self.update_tral_data)
        update_data_button["menu"] = update_menu

        # 新用户数据收集按钮
        collect_data_button = ttk.Button(main_frame, text="新用户数据收集", style="info.TButton", command=self.ask_for_new)
        collect_data_button.grid(row=1, column=0, sticky="nsew", pady=5)

        # 拼团询问按钮
        group_buy_inquiry_button = ttk.Button(main_frame, text="拼团询问/订单通知", style="success.TButton", command=self.group_buy_inquiry)
        group_buy_inquiry_button.grid(row=2, column=0, sticky="nsew", pady=5)

        # 占位按钮（您可以根据需要修改）
        placeholder_button = ttk.Button(main_frame, text="数据展示", style="warning.TButton", command=self.placeholder_function)
        placeholder_button.grid(row=3, column=0, sticky="nsew", pady=5)

    def update_group_buy_data(self):
        messagebox.showinfo("更新拼团数据", "更新拼团数据,请选择excel文件并更新第一页内。")
        print("更新拼团数据")
        data_main = data()
        res = data_main.coupons_data_update()
        messagebox.showinfo("更新拼团数据", res)

    def update_order_data(self):
        messagebox.showinfo("更新订单数据", "更新订单数据,请选择excel文件，并更新第二页内容。")
        print("更新订单数据")
        data_main = data()
        du, res = data_main.order_remind()
        messagebox.showinfo("更新订单数据", f'更新结果：\n重复信息:\n------------\n{du}\n------------\n结果:\n{res}')

    def update_tral_data(self):
        messagebox.showinfo("更新新用户数据数据", "更新订单数据,请选择excel文件，并更新第三页内容。")
        print("更新订单数据")
        data_main = data()
        du, res = data_main.new_member_list()
        messagebox.showinfo("更新订单数据", f'更新结果：\n重复信息:\n------------\n{du}\n------------\n结果:\n{res}')

    def collect_new_user_data(self):
        messagebox.showinfo("开始采集新用户数据", "请选择要发送的群二维码，并上传名单")
        print("收集新用户数据")
        file_path = filedialog.askopenfilename(
            title="选择新用户数据文件",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            print("收集新用户数据")
            print(f"选中的文件: {file_path}")
            main_code.main_collection()
        else:
            print("未选择文件")
            messagebox.showwarning("警告", "未选择文件，无法进行数据采集")

    def collect_new_user_data_loop(self):
        print("收集未回复新用户数据循环")
        loop_nub = simpledialog.askstring("开始重新检查未回复用户", "选择输入循环多少遍：")
        main_code.loop_for_new_member(int(loop_nub))

    def group_buy_inquiry(self):
        print("拼团询问")
        self.open_group_buy_dialog()

    def ask_for_new(self):
        print('新人询问')
        self.ask_for_loop()

    def open_group_buy_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("拼团操作")
        dialog.geometry("300x300")

        invite_button = ttk.Button(dialog, text="📢拼团邀请📣", style="primary.TButton", command=self.send_group_buy_invitation)
        invite_button.pack(fill=tk.X, expand=True, padx=30, pady=10)

        invite_button = ttk.Button(dialog, text="🔂拼团未回复循环🔁", style="primary.TButton", command=self.loop_for_coupons)
        invite_button.pack(fill=tk.X, expand=True, padx=30, pady=10)

        send_order_button = ttk.Button(dialog, text="订单发送", style="success.TButton", command=self.send_order)
        send_order_button.pack(fill=tk.X, expand=True, padx=30, pady=10)

    def ask_for_loop(self):
        dialog = tk.Toplevel(self)
        dialog.title("新人信息收集")
        dialog.geometry("300x200")

        invite_button = ttk.Button(dialog, text="😊开始新人信息收集🛠️", style="primary.TButton", command=self.collect_new_user_data)
        invite_button.pack(fill=tk.X, expand=True, padx=20, pady=20)

        send_order_button = ttk.Button(dialog, text="🔂未回复的新人收集循环🔁", style="success.TButton", command=self.collect_new_user_data_loop)
        send_order_button.pack(fill=tk.X, expand=True, padx=20, pady=20)

    def send_group_buy_invitation(self):
        messagebox.showinfo("拼团/订单", "拼团邀请已经发送。")
        print("拼团邀请已开始，请把微信打开")
        main_code.main_coupons()

    def loop_for_coupons(self):
        print("收集未回复拼团推荐循环")
        loop_nub = simpledialog.askstring("开始重新检查未回复拼团推荐", "选择输入循环多少遍：")
        main_code.loop_for_coupons(int(loop_nub))

    def send_order(self):
        messagebox.showinfo("订单发送", "订单已经发送。")
        print("订单发送已开始，请把微信打开")
        main_code.main_send_order()


    def placeholder_function(self):
        messagebox.showinfo("查看今天的数据", "要查看今天执行的数据吗？")
        print("查看今日数据")
        show_data()





if __name__ == "__main__":
    app = AdaptiveGUI()
    app.mainloop()
