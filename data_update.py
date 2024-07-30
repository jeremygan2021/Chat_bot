import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os



class data:
    def __init__(self):
        self.info_sheet = '拼团信息群发'
        self.order_sheet = '订单信息群发'
        self.new_member = '新用户微信名单'

    def coupons_data_update(self):
        # 使用Tkinter打开文件选择对话框
        root = Tk()
        root.withdraw()  # 隐藏主窗口
        excel_file = askopenfilename(filetypes=[("Excel files", "*.xlsx")], title="选择Excel文件")
        root.destroy()

        if not excel_file:
            print("未选择文件，操作已取消。")
            return

        # 假设工作表名称为'Sheet1'


        # 使用pandas读取Excel文件
        df = pd.read_excel(excel_file, sheet_name=self.info_sheet)

        # 打印列名以确认确切名称
        print("Excel文件中的列名：")
        print(df.columns)

        # 提取特定列并重命名
        df_csv = pd.DataFrame()
        df_csv['name'] = df['微信名']
        df_csv['date'] = df['日期']
        df_csv['target'] = df['目的']
        df_csv['info'] = df['拼团活动内容']
        df_csv['index'] = 1
        df_csv['coupons_link'] = df['拼团活动链接']
        df_csv['consumer_tag'] = df['客户类型注释']
        # 确认客户类型注释列名是否正确

        # 将DataFrame写入CSV文件，假设文件名为'output.csv'
        csv_file = 'daily_tral/run.csv'
        df_csv.to_csv(csv_file, index=False)
        res = f"拼团数据已成功从{excel_file}搬运到{csv_file}"
        print(res)
        return res

    def order_remind(self):
        root = Tk()
        root.withdraw()  # 隐藏主窗口
        excel_file = askopenfilename(filetypes=[("Excel files", "*.xlsx")], title="选择Excel文件")
        root.destroy()

        if not excel_file:
            print("未选择文件，操作已取消。")
            return

        # 使用pandas读取Excel文件
        df = pd.read_excel(excel_file, sheet_name=self.order_sheet)
        print("Excel文件中的列名：")
        print(df.columns)

        # 创建新的DataFrame并统一日期格式
        df_csv = pd.DataFrame()
        df_csv['date'] = pd.to_datetime(df['日期']).dt.strftime('%Y/%m/%d')
        df_csv['name'] = df['微信名']
        df_csv['order_info'] = df['订单详情']
        df_csv['order_id'] = df['单号']
        df_csv['status'] = 'off'

        # 指定CSV文件路径
        csv_file = 'daily_tral/order.csv'

        # Check if CSV file already exists
        if os.path.exists(csv_file):
            # If file exists, read existing data
            existing_df = pd.read_csv(csv_file)

            # Check for duplicates without considering 'status'
            merge_columns = ['date', 'name', 'order_info', 'order_id']
            duplicates = df_csv.merge(existing_df[merge_columns], how='inner', on=merge_columns)
            if not duplicates.empty:
                print("找到以下的重复数据列出:")
                print('-------------------')
                print(duplicates)
                print('-------------------')
                print("这些重复数据不会被添加.")

            # Keep only non-duplicate data
            df_csv = df_csv.merge(existing_df[merge_columns], how='left', indicator=True)
            df_csv = df_csv[df_csv['_merge'] == 'left_only'].drop('_merge', axis=1)

            # Add new data to the end of existing data
            updated_df = pd.concat([existing_df, df_csv], ignore_index=True)
        else:
            # If file doesn't exist, use new data directly
            updated_df = df_csv

        # Write updated DataFrame to CSV file
        res = f"-------------------\n订单数据成功从添加 {excel_file} 到 {csv_file}\n-------------------\n一共增加新数据数量: {len(df_csv)}"

        updated_df.to_csv(csv_file, index=False)
        print(res)
        return duplicates, res


    def new_member_list(self):
        duplicates = pd.DataFrame()  # 初始化 duplicates
        root = Tk()
        root.withdraw()  # 隐藏主窗口
        excel_file = askopenfilename(filetypes=[("Excel files", "*.xlsx")], title="选择Excel文件")
        root.destroy()

        if not excel_file:
            print("未选择文件，操作已取消。")
            return duplicates, "操作已取消"  # 返回空的 duplicates 和消息

        # 使用pandas读取Excel文件
        df = pd.read_excel(excel_file, sheet_name=self.new_member)
        print("Excel文件中的列名：")
        print(df.columns)

        # 创建新的DataFrame并统一日期格式
        df_csv = pd.DataFrame()
        df_csv['date'] = pd.to_datetime(df['日期']).dt.strftime('%Y/%m/%d')
        df_csv['name'] = df['微信名']
        df_csv['consumer_tag'] = df['客户类型注释']
        df_csv['status'] = 'off'

        # 指定CSV文件路径
        csv_file = 'daily_tral/new_member.csv'

        # Check if CSV file already exists
        if os.path.exists(csv_file):
            # If file exists, read existing data
            existing_df = pd.read_csv(csv_file)

            # Check for duplicates without considering 'status'
            merge_columns = ['date', 'name', 'consumer_tag']
            duplicates = df_csv.merge(existing_df[merge_columns], how='inner', on=merge_columns)
            if not duplicates.empty:
                print("找到以下的重复数据列出:")
                print('-------------------')
                print(duplicates)
                print('-------------------')
                print("这些重复数据不会被添加.")

            # Keep only non-duplicate data
            df_csv = df_csv.merge(existing_df[merge_columns], how='left', indicator=True)
            df_csv = df_csv[df_csv['_merge'] == 'left_only'].drop('_merge', axis=1)

            # Add new data to the end of existing data
            updated_df = pd.concat([existing_df, df_csv], ignore_index=True)
        else:
            # If file doesn't exist, use new data directly
            updated_df = df_csv

        # Write updated DataFrame to CSV file
        res = f"-------------------\n订单数据成功从添加 {excel_file} 到 {csv_file}\n-------------------\n一共增加新数据数量: {len(df_csv)}"

        updated_df.to_csv(csv_file, index=False)
        print(res)
        return duplicates, res

#
#
# cs = data()
# cs.order_remind()