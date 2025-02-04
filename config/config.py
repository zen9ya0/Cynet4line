import os

# 定義 client_ids 列表
client_ids = []

# 讀取 client_ids.conf 文件
try:
    with open('config/client_ids.conf', 'r') as file:
        # 將每一行的值去除空白後加入 client_ids 列表
        client_ids = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print("client_ids.conf 文件未找到。請確保文件存在於 config 目錄中。")
    exit(1)

# 其他配置
user_name = os.getenv('Cynet_user_name')
password = os.getenv('Cynet_password')
time_offset_minutes = int(os.getenv('TIME_OFFSET_MINUTES', 5))  # 默認為 5 分鐘
limit = 999  # 設置返回的最大項目數
offset = 1   # 設置從哪個項目開始返回

if not client_ids:
    print("client_ids.conf 文件中沒有有效的 client_id。")
    exit(1)
