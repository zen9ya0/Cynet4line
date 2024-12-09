import http.client
from config.config import client_id, time_offset_minutes  # 從 config.py 中導入 client_id 和 time_offset_minutes
from config.GetToken import access_token  # 假設你已經在 GetToken.py 中獲取了 access_token
from datetime import datetime, timedelta
import json
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)  # 將日誌級別設置為 INFO
logger = logging.getLogger(__name__)

def fetch_alerts(client_id, access_token, time_offset_minutes):
    """從 Cynet API 獲取 Alerts 數據"""
    last_seen = (datetime.utcnow() - timedelta(minutes=time_offset_minutes)).isoformat() + "Z"
    url = f"/api/alerts?LastSeen={last_seen}"
    conn = http.client.HTTPSConnection("mssp.api.cynet.com")

    headers = {
        'client_id': client_id,
        'access_token': access_token,
        'Accept': "application/json"
    }

    try:
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        if res.status != 200:
            raise Exception(f"API 請求失敗，狀態碼: {res.status}")
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        logger.error(f"獲取數據時發生錯誤: {e}")
        return {}

def load_last_client_db_ids():
    """加載上次的 ClientDbId 值，這裡假設從文件或其他存儲中加載"""
    # 這裡可以根據實際情況實現加載邏輯
    # 示例：返回一個包含上次 ClientDbId 的集合
    return {0}  # 這裡應該替換為實際的加載邏輯

def main():
    # 獲取 Alerts 數據
    alerts_data = fetch_alerts(client_id, access_token, time_offset_minutes)

    # 檢查是否存在有效的警報數據
    if not alerts_data or "Entities" not in alerts_data:
        return  # 如果沒有有效的數據，則不打印任何內容

    # 加載上次的 ClientDbId 值
    last_client_db_ids = load_last_client_db_ids()

    # 將所需的訊息轉換為純文字格式
    alerts_text = ""
    for entity in alerts_data["Entities"]:
        # 獲取 ClientDbId 和其他所需欄位
        client_db_id = entity.get("ClientDbId")  # 獲取 ClientDbId
        severity = entity.get("Severity")  # 獲取 Severity
        incident_name = entity.get("IncidentName")  # 獲取 IncidentName
        Host_Ip = entity.get("HostIp")  # 獲取 HostIp
        Host_Name = entity.get("HostName")  # 獲取 HostName
        CommandLine = entity.get("CommandLine")  # 獲取 CommandLine
        Path = entity.get("Path")  # 獲取 Path


        
        # 只有在 ClientDbId 不在上次的集合中時才添加到輸出文本
        if client_db_id is not None and client_db_id not in last_client_db_ids:
            alerts_text += f"IncidentName: {incident_name}\nAlert# {client_db_id}\nSeverity: {severity}\n主機IP: {Host_Ip}\n主機名稱: {Host_Name}\nCommandLine: {CommandLine}\nPath: {Path}\n"

    # 只有在有新的警報時才打印
    if alerts_text:
        print(alerts_text)  # 顯示純文字格式的警報

if __name__ == "__main__":
    main()
