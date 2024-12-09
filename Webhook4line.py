from flask import Flask, request, abort
import subprocess
import logging
import os
import threading
import time
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定 LINE Bot API
access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
secret = os.getenv('LINE_CHANNEL_SECRET')

if access_token is None or secret is None:
    logger.error("請確保環境變數已正確設置。")
    exit(1)

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 儲存最新的警報信息
latest_alerts = ""

def fetch_alerts():
    global latest_alerts
    while True:
        #logger.info("執行 GetLastAlerts.py...")
        result = subprocess.run(['python3', 'GetLastAlerts.py'], capture_output=True, text=True)

        if result.returncode != 0:
            #logger.error(f"執行 GetLastAlerts.py 時出錯: {result.stderr}")
            latest_alerts = "執行 GetLastAlerts.py 時出錯"
        else:
            output = result.stdout.strip()
            #logger.info(f"從 GetLastAlerts.py 獲取的輸出: {output}")

            # 檢查輸出是否為純文字
            if isinstance(output, str) and output:
                # 將純文字發送到 Line Bot
                line_bot_api.broadcast(TextSendMessage(text=output))
            #else:
            #    logger.error("格式錯誤: 接收到的資料不是純文字。")
            #    logger.error("格式錯誤: 接收到的資料不是純文字。")

        time.sleep(180)  # 每 5 分鐘執行一次

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']

    # 驗證簽名
    try:
        handler.handle(body, signature)
        #logger.info("簽名驗證成功。")
    except InvalidSignatureError:
        logger.error("無效的簽名。請求被中止。")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    #logger.info(f"收到消息: {event.message.text}")
    # 回應用戶的消息
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="收到您的消息！"))

if __name__ == "__main__":
    # 啟動定時任務
    alert_thread = threading.Thread(target=fetch_alerts)
    alert_thread.daemon = True
    alert_thread.start()

    app.run(debug=True)
