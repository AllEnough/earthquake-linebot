# quake_api.py
import requests
from config import CWA_API_KEY
from quake_parser import parse_quake_record
from logger import logger

def fetch_latest_quake():
    url_minor = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={CWA_API_KEY}'
    url_major = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={CWA_API_KEY}'
    
    latest = None
    for u in [url_minor, url_major]:
        try:
            response = requests.get(u)
            data = response.json()
            record = parse_quake_record(data['records']['Earthquake'][0])
            if record and (latest is None or record['origin_time'] > latest['origin_time']):
                latest = record
        except Exception as e:
            logger.error(f"⚠️ 地震資料解析錯誤：{e}")

    return latest
