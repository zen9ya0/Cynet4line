import http.client
import json
import os  # 用於讀取環境變數

# 從環境變數中讀取 Cynet_user_name 和 Cynet_password
user_name = os.getenv('Cynet_user_name')
password = os.getenv('Cynet_password')

if user_name is None or password is None:
    print("請確保環境變數 Cynet_user_name 和 Cynet_password 已正確設置。")
    exit(1)

conn = http.client.HTTPSConnection("mssp.api.cynet.com")

payload = json.dumps({
    "user_name": user_name,
    "password": password
})

headers = {
    'Content-Type': "application/json",
    'Accept': "application/json"
}

try:
    conn.request("POST", "/api/account/token", payload, headers)
    res = conn.getresponse()
    
    # 打印響應狀態碼
    #print(f"Response status: {res.status}")
    
    data = res.read()
    response_json = json.loads(data.decode("utf-8"))
    
    # 獲取 access_token
    access_token = response_json.get("access_token")
    #print(f"Access Token: {access_token}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
