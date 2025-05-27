import requests
import time
from datetime import datetime
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest

# ✅ 寫死 token（你可以改成從環境變數讀取）
LINE_CHANNEL_ACCESS_TOKEN = 'p0Je4vYvQ5A3UhZbxMrqhex1gznrICRHBN7Kd3qcb87HegwHNCVDmqThV1I6VfDt1rsmTFUAiy+ykRXyjnGssJaZJ4Baoz0Z9YBZJ7NDO+K8XytQjxXFkz4TbQTSjhtqZQQX1E+TofEU99qLxLn6nAdB04t89/1O/w1cDnyilFU='
USER_ID = "U7a28ed369cc94af4c0ff6f811b59e2ad"

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

def push_message(text):
    message = TextMessage(text="🎉 測試訊息 from Railway 雲端！")
    line_bot_api.push_message(to=USER_ID, messages=[message])

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        try:
            message = TextMessage(text=text)
            body = PushMessageRequest(to=USER_ID, messages=[message])
            line_bot_api.push_message(push_message_request=body)
            print("✅ 已推播訊息")
        except Exception as e:
            print("❌ 推播失敗：", e)


def get_latest_quake():
    url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization=CWA-9A20417D-4DB8-4A27-A638-1814ECE1CBAF'
    response = requests.get(url)
    data = response.json()

    try:
        eq = data['records']['Earthquake'][0]
        info = eq['EarthquakeInfo']
        return {
            'origin_time': info['OriginTime'],
            'location': info['Epicenter']['Location'],
            'depth': info['FocalDepth'],
            'magnitude': info['EarthquakeMagnitude']['MagnitudeValue'],
            'report': eq['ReportContent'],
            'link': eq['Web']
        }
    except Exception as e:
        print("⚠️ 地震資料解析錯誤：", e)
        return None

# ✅ 初始狀態
last_quake_time = None

# ✅ 每五分鐘檢查一次
while True:
    quake = get_latest_quake()
    if quake:
        if quake['origin_time'] != last_quake_time:
            last_quake_time = quake['origin_time']
            msg = f"""📢 新地震速報！
時間：{quake['origin_time']}
地點：{quake['location']}
深度：{quake['depth']} 公里
規模：{quake['magnitude']} 芮氏
➡️ 詳情：{quake['link']}
"""
            push_message(msg)
        else:
            print(f"🔄 尚無新地震，最後地震：{last_quake_time}")
    else:
        print("⚠️ 抓取地震資料失敗")

    time.sleep(300)
