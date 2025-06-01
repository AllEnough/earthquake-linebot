# quake_parser.py
from datetime import datetime, UTC
from logger import logger

def parse_quake_record(eq):
    try:
        info = eq['EarthquakeInfo']
        quake = {
            'origin_time': datetime.strptime(info['OriginTime'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC),
            'epicenter': info['Epicenter']['Location'],
            'depth': info['FocalDepth'],
            'magnitude': info['EarthquakeMagnitude']['MagnitudeValue'],
            'report': eq['ReportContent'],
            'link': eq['Web']
        }

        # 檢查欄位完整性
        if None in quake.values():
            logger.warning(f"⚠️ 地震資料欄位不完整，跳過：{quake}")
            return None

        return quake

    except KeyError as e:
        logger.error(f"❌ Key 錯誤，跳過地震紀錄：{e}")
    except Exception as e:
        logger.error(f"❌ 地震資料解析錯誤：{e}")

    return None
