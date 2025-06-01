# quake_api.py
import requests
from config import CWA_API_KEY
from quake_parser import parse_quake_record
from logger import logger

def fetch_latest_quake():
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={CWA_API_KEY}'
    try:
        response = requests.get(url)
        data = response.json()
        records = data['records']['Earthquake']
        return parse_quake_record(records[0])
    except Exception as e:
        logger.error(f"⚠️ 地震資料解析錯誤：{e}")
        return None
