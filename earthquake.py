print("🚀 程式開始執行！")
import requests
import json
import pandas as pd

# 地震資料 API_KEY
API_KEY = 'CWA-9A20417D-4DB8-4A27-A638-1814ECE1CBAF'

# 台灣地震資料 API
url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={API_KEY}'

print("🌐 開始連線氣象局 API")
response = requests.get(url)
print("✅ API 回應成功")

try:
    data = response.json()
    print("📦 成功轉換為 JSON")
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print("❌ JSON 轉換失敗：", e)

try:
    records = data['records']['Earthquake']
    print(f"🔍 抓到 {len(records)} 筆地震資料")
except Exception as e:
    print("❌ 抓取 earthquake 資料失敗：", e)

# 抽取你需要的欄位（日期、時間、震央、深度、規模）
earthquake_list = []

for eq in records:
    try:
        info = eq['EarthquakeInfo']
        quake = {
            'origin_time': info['OriginTime'],  # 發生時間
            'epicenter': info['Epicenter']['Location'],  # 地震中心
            'depth': info['FocalDepth'],  # 深度（公里）
            'magnitude': info['EarthquakeMagnitude']['MagnitudeValue']  # 規模
        }

        # 確保四個欄位都存在
        if None not in quake.values():
            earthquake_list.append(quake)
        else:
            print("⚠️ 資料不完整，跳過：", quake)

    except KeyError as e:
        print("❌ 資料格式錯誤，跳過此筆：", e)
        continue

print("📄 資料整理完成，共有", len(earthquake_list), "筆")

df = pd.DataFrame(earthquake_list)
print("🖨️ 預覽資料：")
print(df.head())  # 顯示前幾筆資料

#--------------------------------------

# 將資料寫入 MongoDB
from pymongo import MongoClient, errors

print("🔗 嘗試連接 MongoDB Atlas")
MONGO_URI = "mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# 替換成你的 MongoDB 連線字串（本機或 Atlas）
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    # 強制測試連線（沒通會觸發錯誤）
    client.server_info()  
    print("✅ 成功連線 MongoDB Atlas")
    
    db = client['earthquake_db']
    collection = db['earthquakes']

    count = 0
    for quake in earthquake_list:
        try:
            if collection.count_documents({'origin_time': quake['origin_time']}) == 0:
                collection.insert_one(quake)
                count += 1

        except Exception as e:
            print("❌ 寫入失敗：", quake, e)
    
    print(f"✅ 寫入完成，共新增 {count} 筆資料")

except errors.ServerSelectionTimeoutError as e:
    print("❌ 無法連接 MongoDB Atlas：", e)

except errors.PyMongoError as e:
    print("❌ 寫入 MongoDB 發生錯誤：", e)
