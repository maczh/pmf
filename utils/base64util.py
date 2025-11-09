import base64
from typing import Optional


def base64_encode(s: str) -> str:
    """Base64编码"""
    return base64.b64encode(s.encode()).decode()


def base64_decode(s: str) -> str:
    """Base64解码"""
    try:
        return base64.b64decode(s).decode()
    except Exception as e:
        print(f"Base64解码错误: {str(e)}")
        return ""