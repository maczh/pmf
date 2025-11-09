import hmac
import hashlib
import base64

def hmac_sha1(key: str, data: str) -> bytes:
    """HMAC-SHA1计算"""
    return hmac.new(key.encode(), data.encode(), hashlib.sha1).digest()

def hmac_sha256(key: str, data: str) -> bytes:
    """HMAC-SHA256计算"""
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).digest()

def hmac_sha1_hex(key: str, data: str) -> str:
    """HMAC-SHA1结果转16进制"""
    return hmac_sha1(key, data).hex()

def hmac_sha1_base64(key: str, data: str) -> str:
    """HMAC-SHA1结果转Base64"""
    return base64.b64encode(hmac_sha1(key, data)).decode()

def hmac_sha256_hex(key: str, data: str) -> str:
    """HMAC-SHA256结果转16进制"""
    return hmac_sha256(key, data).hex()

def hmac_sha256_base64(key: str, data: str) -> str:
    """HMAC-SHA256结果转Base64"""
    return base64.b64encode(hmac_sha256(key, data)).decode()