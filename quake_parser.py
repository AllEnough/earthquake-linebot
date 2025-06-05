# quake_parser.py
from datetime import datetime, UTC
from logger import logger
from geocode_utils import get_coordinates_from_text


def parse_quake_record(eq):
    try:
        info = eq['EarthquakeInfo']
        epicenter_info = info['Epicenter']
        epicenter = epicenter_info['Location']

        quake = {
            'origin_time': datetime.strptime(info['OriginTime'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC),
            'epicenter': info['Epicenter']['Location'],
            'depth': info['FocalDepth'],
            'magnitude': info['EarthquakeMagnitude']['MagnitudeValue'],
            'report': eq['ReportContent'],
            'link': eq['Web']
        }

        # 先從氣象局資料嘗試取得經緯度
        lat = (
            epicenter_info.get('EpicenterLatitude')
            or epicenter_info.get('Latitude')
            or epicenter_info.get('Lat')
        )
        lon = (
            epicenter_info.get('EpicenterLongitude')
            or epicenter_info.get('Longitude')
            or epicenter_info.get('Lon')
        )

        if lat is not None and lon is not None:
            try:
                quake['lat'] = float(lat)
                quake['lon'] = float(lon)
                logger.info(
                    f"📍 已從氣象局資料取得經緯度：{epicenter} → ({quake['lat']}, {quake['lon']})"
                )
            except Exception:
                lat = lon = None

        # 若資料中沒有經緯度，再透過 Google Maps API 補足
        if lat is None or lon is None:
            lat, lon = get_coordinates_from_text(epicenter)
            if lat and lon:
                quake['lat'] = lat
                quake['lon'] = lon

        # 檢查欄位完整性
        if None in [quake['origin_time'], quake['epicenter'], quake['depth'], quake['magnitude']]:
            logger.warning(f"⚠️ 地震資料欄位不完整，跳過：{quake}")
            return None

        return quake

    except KeyError as e:
        logger.error(f"❌ Key 錯誤，跳過地震紀錄：{e}")
    except Exception as e:
        logger.error(f"❌ 地震資料解析錯誤：{e}")

    return None
