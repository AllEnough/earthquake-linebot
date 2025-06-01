# font_utils.py
import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as fm
from logger import logger

def use_custom_font_from_file(font_path: str):
    base_dir = os.path.dirname(__file__)  # 取得當前檔案所在資料夾
    font_path = os.path.join(base_dir, "fonts/NotoSansTC-Regular.ttf")

    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        logger.info(f"✅ 使用中文字體：{font_prop.get_name()}")
    else:
        logger.error("⚠️ 找不到字體：", font_path)
        plt.rcParams['font.family'] = 'sans-serif'
