import hashlib
import os
from typing import Tuple, Optional

def sha1(src: str) -> str:
    """SHA1摘要"""
    return hashlib.sha1(src.encode()).hexdigest()

def sha256(src: str) -> str:
    """SHA256摘要"""
    return hashlib.sha256(src.encode()).hexdigest()

def file_sha256(filename: str) -> Tuple[str, Optional[Exception]]:
    """
    计算文件SHA256
    :return: (SHA256值, 错误信息)
    """
    try:
        with open(filename, 'rb') as f:
            sha256_hash = hashlib.sha256()
            while chunk := f.read(4096):
                sha256_hash.update(chunk)
            return sha256_hash.hexdigest(), None
    except Exception as e:
        return "", e