from Crypto.Cipher import DES, DES3
from Crypto.Util.Padding import pad, unpad
import base64

def des_encrypt(orig_data: bytes, key: bytes) -> bytes:
    """DES加密（CBC模式）"""
    cipher = DES.new(key, DES.MODE_CBC, key)
    padded_data = pad(orig_data, DES.block_size)
    return cipher.encrypt(padded_data)

def des_decrypt(crypted: bytes, key: bytes) -> bytes:
    """DES解密（CBC模式）"""
    cipher = DES.new(key, DES.MODE_CBC, key)
    data = cipher.decrypt(crypted)
    return unpad(data, DES.block_size)

def des_ecb_encrypt(orig_data: bytes, key: bytes) -> bytes:
    """DES加密（ECB模式）"""
    cipher = DES.new(key, DES.MODE_ECB)
    padded_data = pad(orig_data, DES.block_size)
    return cipher.encrypt(padded_data)

def des_ecb_decrypt(crypted: bytes, key: bytes) -> bytes:
    """DES解密（ECB模式）"""
    cipher = DES.new(key, DES.MODE_ECB)
    data = cipher.decrypt(crypted)
    return unpad(data, DES.block_size)

def des_encrypt_str(data: str, key: str) -> str:
    """DES加密字符串"""
    try:
        key_bytes = key.encode('utf-8')
        data_bytes = data.encode('utf-8')
        encrypted = des_encrypt(data_bytes, key_bytes)
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"DES加密错误: {e}")
        return ""

def des_decrypt_str(data: str, key: str) -> str:
    """DES解密字符串"""
    try:
        key_bytes = key.encode('utf-8')
        data_bytes = base64.b64decode(data)
        decrypted = des_decrypt(data_bytes, key_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"DES解密错误: {e}")
        return ""