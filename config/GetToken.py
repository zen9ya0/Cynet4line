import http.client
import json
from config.config import user_name, password 

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
