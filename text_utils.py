# text_utils.py

def normalize_tai(text: str) -> str:
    """Replace common simplified forms like '台' with '臺'."""
    return text.replace("台", "臺")