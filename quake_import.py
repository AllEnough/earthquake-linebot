import requests
import json
from pymongo import MongoClient, errors
import certifi

API_KEY = 'CWA-9A20417D-4DB8-4A27-A638-1814ECE1CBAF'
MONGO_URI = "mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
db = client['earthquake_db']
collection = db['earthquakes']

def fetch_and_store_earthquake_data():
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={API_KEY}'
    print("🌐 嘗試連線中央氣象局 API...")
    try:
        response = requests.get(url)
        data = response.json()
        records = data['records']['Earthquake']
        print(f"✅ 抓到 {len(records)} 筆地震資料")
    except Exception as e:
        print("❌ 抓取或解析 API 資料失敗：", e)
        return

    count = 0
    for eq in records:
        try:
            info = eq['EarthquakeInfo']
            quake = {
                'origin_time': info['OriginTime'],
                'epicenter': info['Epicenter']['Location'],
                'depth': info['FocalDepth'],
                'magnitude': info['EarthquakeMagnitude']['MagnitudeValue'],
                'report': eq['ReportContent'],
                'link': eq['Web']
            }

            if None in quake.values():
                print("⚠️ 資料不完整，跳過：", quake)
                continue

            if collection.count_documents({'origin_time': quake['origin_time']}) == 0:
                collection.insert_one(quake)
                count += 1
        except KeyError as e:
            print("❌ Key 錯誤，跳過一筆：", e)
        except Exception as e:
            print("❌ 寫入 MongoDB 錯誤：", e)

    print(f"✅ 資料庫更新完成，共新增 {count} 筆地震資料")

if __name__ == "__main__":
    fetch_and_store_earthquake_data()
