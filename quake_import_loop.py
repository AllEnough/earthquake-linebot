import time
import threading
from quake_import import fetch_and_store_earthquake_data

def run_quake_import_loop(interval_minutes=5):
    while True:
        print("🌀 執行定期地震資料匯入...")
        fetch_and_store_earthquake_data()
        print(f"⏳ 等待 {interval_minutes} 分鐘後再次執行...\n")
        time.sleep(interval_minutes * 60)

def start_background_quake_import():
    t = threading.Thread(target=run_quake_import_loop, daemon=True)
    t.start()
    print("🌍 地震資料匯入已在背景中啟動。")