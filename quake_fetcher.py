#地震資料獲取
import requests

# 紀錄最後一次推播的地震時間
last_quake_time = None
def get_latest_quake():
    url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization=CWA-9A20417D-4DB8-4A27-A638-1814ECE1CBAF'
    response = requests.get(url)
    data = response.json()

    try:
        eq = data['records']['Earthquake'][0]
        info = eq['EarthquakeInfo']
        return {
            'origin_time': info['OriginTime'],
            'epicenter': info['Epicenter']['Location'],
            'depth': info['FocalDepth'],
            'magnitude': info['EarthquakeMagnitude']['MagnitudeValue'],
            'report': eq['ReportContent'],
            'link': eq['Web']
        }
    except Exception as e:
        print("⚠️ 地震資料解析錯誤：", e)
        return None
