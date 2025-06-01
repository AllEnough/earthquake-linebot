# font_utils.py
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
from logger import logger

def set_chinese_font():
    """
    設定 Matplotlib 中文字體，優先使用 Noto Sans TC，
    否則回退至常見中文字體清單。
    """
    font_candidates = [
        "Noto Sans TC",
        "Microsoft JhengHei",
        "PingFang TC",
        "Heiti TC",
        "Arial Unicode MS",
        "SimHei"
    ]

    found = False
    for font in font_candidates:
        try:
            plt.rcParams["font.family"] = font
            plt.figure()
            plt.text(0.5, 0.5, "中文測試", fontsize=12)
            plt.close()
            logger.info(f"✅ 使用中文字體：{font}")
            found = True
            break
        except Exception:
            continue

    if not found:
        logger.warning("⚠️ 找不到任何中文字體，中文圖表可能會出現亂碼")

def use_custom_font_from_file(font_path: str):
    """
    直接指定字體檔案（.ttf 或 .otf）使用
    """
    try:
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = font_prop.get_name()
        logger.info(f"✅ 成功載入自訂字體：{font_prop.get_name()}")
    except Exception as e:
        logger.error(f"❌ 載入字體檔失敗：{e}")
