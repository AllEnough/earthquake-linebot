# logger.py
import logging
import os

# 建立 logs 資料夾（若尚未存在）
os.makedirs("logs", exist_ok=True)

# 建立 logger 實例
logger = logging.getLogger("earthquake_logger")
logger.setLevel(logging.INFO)

# 建立檔案處理器：寫入 logs/app.log
file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 建立 console 處理器：輸出到畫面
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 設定日誌格式
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 將處理器加到 logger 上
logger.addHandler(file_handler)
logger.addHandler(console_handler)
