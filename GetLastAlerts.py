import http.client
import json
import re
import logging
import argparse
from config.config import client_ids, time_offset_minutes  # 從 config.py 中導入 client_ids 和 time_offset_minutes
from config.GetToken import access_token  # 假設你已經在 GetToken.py 中獲取了 access_token
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

# 設定日誌
logging.basicConfig(level=logging.INFO)  # 將日誌級別設置為 INFO
logger = logging.getLogger(__name__)

def fetch_alerts(client_id, access_token, time_offset_minutes):
    """從 Cynet API 獲取 Alerts 數據"""
    current_time = datetime.now(timezone.utc)
    last_seen = (current_time - timedelta(minutes=int(time_offset_minutes))).strftime('%Y-%m-%d %H:%M:%S')
    
    # 調試輸出
    #logger.info(f"Current time (UTC): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    #logger.info(f"Last seen time: {last_seen}")
    
    params = {'LastSeen': last_seen}
    url = f"/api/alerts?{urlencode(params)}"
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

def clean_alert(alert):
    """清理 Alert 數據並保留所需字段"""
    for key in alert:
        if isinstance(alert[key], str):  # 確保值是字符串
            # 替換多餘的反斜線為單個反斜線
            alert[key] = re.sub(r'\\\\+', r'\\', alert[key])  # 注意替換時的原始字符串 r'\\'
        else:
            logger.warning(f"警報中的 {key} 不是字符串，跳過處理。")
    return alert

def load_last_client_db_ids():
    """加載上次的 ClientDbId 值"""
    try:
        with open('last_client_db_ids.txt', 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_client_db_ids(client_db_ids):
    """保存當前的 ClientDbId 值"""
    with open('last_client_db_ids.txt', 'w') as f:
        for client_db_id in client_db_ids:
            f.write(f"{client_db_id}\n")

def main():
    # 設置命令行參數解析
    parser = argparse.ArgumentParser(description='Fetch alerts from Cynet API.')
    parser.add_argument('-id', '--client_id', type=str, help='Specify a client ID to fetch alerts for a single client.')
    args = parser.parse_args()

    # 使用命令行參數中的 client_id 或默認的 client_ids 列表
    if args.client_id:
        selected_client_ids = [args.client_id]
    else:
        selected_client_ids = client_ids

    # 加載上次的 ClientDbId 值
    last_client_db_ids = load_last_client_db_ids()
    current_client_db_ids = set()  # 用於存儲當前的 ClientDbId
    processed_client_db_ids = set()  # 用於追踪已處理的 ClientDbId

    # 遍歷每個 client_id 並獲取 Alerts 數據
    for client_id in selected_client_ids:
        alerts_data = fetch_alerts(client_id, access_token, time_offset_minutes)
        
        # 檢查 Entities 是否存在且有資料
        if "Entities" in alerts_data and alerts_data["Entities"]:
            # 將所需的訊息轉換為純文字格式
            alerts_text = ""
            for entity in alerts_data["Entities"]:
                # 獲取所需欄位
                client_db_id = entity.get("ClientDbId")
                
                # 檢查 ClientDbId 是否已經處理過
                if client_db_id is None or client_db_id in processed_client_db_ids:
                    continue

                # 如果是新的 ClientDbId 且不在上次的集合中
                if client_db_id not in last_client_db_ids:
                    severity = entity.get("Severity")
                    incident_name = entity.get("IncidentName")
                    host_ip = entity.get("HostIp")
                    host_name = entity.get("HostName")
                    command_line = entity.get("CommandLine")
                    path = entity.get("Path")
                    eps_last_seen_local = entity.get("EpsLastSeenLocal")

                    alerts_text += (
                        f"警報名稱: {incident_name}\n"
                        f"警報編號: {client_db_id}\n"
                        f"警報嚴重性: {severity}\n"
                        f"主機IP: {host_ip}\n"
                        f"主機名稱: {host_name}\n"
                        f"命令行: {command_line}\n"
                        f"路徑: {path}\n"
                        f"警報時間: {eps_last_seen_local}\n"
                        "-------------------------\n"
                    )
                
                # 將 ClientDbId 添加到已處理集合和當前集合中
                processed_client_db_ids.add(client_db_id)
                current_client_db_ids.add(client_db_id)

            # 只在這裡輸出一次
            if alerts_text:
                print(f"{client_id} 的新警報:\n{alerts_text.rstrip()}")
            else:
                #print(f"{client_id}: Nothing update")
                pass
        else:
            #print(f"{client_id}: Nothing update")
            pass

    # 保存當前的 ClientDbId
    save_client_db_ids(current_client_db_ids)

if __name__ == "__main__":
    main()
