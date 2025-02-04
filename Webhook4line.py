from flask import Flask, request, abort
import subprocess
import logging
import os
import threading
import time
import json
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging.models import (
    TextMessage,
    Message,
    BroadcastRequest,
    ReplyMessageRequest
)

app = Flask(__name__)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定 LINE Bot API
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

if channel_access_token is None or channel_secret is None:
    logger.error("請確保環境變數已正確設置。")
    exit(1)

# 初始化 LINE API 客戶端
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

# 儲存最新的警報信息
latest_alerts = ""

def split_message(text, max_length=4000):
    """將長消息分割成較小的部分"""
    messages = []
    while text:
        if len(text) <= max_length:
            messages.append(text)
            break
        # 尋找合適的分割點
        split_point = text.rfind('\n', 0, max_length)
        if split_point == -1:
            split_point = max_length
        messages.append(text[:split_point])
        text = text[split_point:].lstrip()
    return messages

def fetch_alerts():
    global latest_alerts
    while True:
        result = subprocess.run(['python3', 'GetLastAlerts.py'], capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"執行 GetLastAlerts.py 時出錯: {result.stderr}")
        else:
            output = result.stdout.strip()
            if output:
                try:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 分割長消息
                        messages = split_message(output)
                        for message in messages:
                            if message.strip():  # 確保消息不是空的
                                request = BroadcastRequest(
                                    messages=[TextMessage(text=message)]
                                )
                                line_bot_api.broadcast(request)
                                time.sleep(1)  # 添加短暫延遲以避免過快發送
                except Exception as e:
                    logger.error(f"發送消息時發生錯誤: {e}")
                    logger.error(f"錯誤詳情: {str(e)}")

        time.sleep(180)  # 每 3 分鐘執行一次

@app.route("/", methods=['POST'])
def linebot():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        logger.error(f"處理 webhook 時發生錯誤: {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="收到您的消息！")]
        )
        line_bot_api.reply_message(request)

if __name__ == "__main__":
    # 啟動定時任務
    alert_thread = threading.Thread(target=fetch_alerts)
    alert_thread.daemon = True
    alert_thread.start()

    app.run(debug=True)
