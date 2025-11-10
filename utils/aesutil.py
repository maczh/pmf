# python
import base64
import logging
from Crypto.Cipher import AES
from typing import Literal
def pkcs_padding(data: bytes, block_size: int, mode: Literal["pkcs5", "pkcs7"] = "pkcs7") -> bytes:
    if mode == "pkcs5":
        pad_len = 8 - (len(data) % 8)
    else:  # pkcs7
        pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len

def aes_encrypt_base64(data: bytes, key: bytes, iv: bytes = None, mode: Literal["CBC", "ECB"] = "CBC", padding: Literal["pkcs5", "pkcs7"] = "pkcs7") -> str:
    encrypted = aes_encrypt(data, key, iv, mode, padding)
    return base64.b64encode(encrypted).decode('utf-8')

def aes_decrypt_base64(encrypted_b64: str, key: bytes, iv: bytes = None, mode: Literal["CBC", "ECB"] = "CBC", padding: Literal["pkcs5", "pkcs7"] = "pkcs7") -> bytes:
    encrypted = base64.b64decode(encrypted_b64)
    return aes_decrypt(encrypted, key, iv, mode, padding)

def pkcs_unpadding(data: bytes, mode: Literal["pkcs5", "pkcs7"] = "pkcs7") -> bytes:
    if not data:
        raise ValueError("解密错误")
    pad_len = data[-1]
    if pad_len <= 0 or pad_len > len(data):
        raise ValueError("解密错误")
    print(f"pad_len: {pad_len}")
    # if mode == "pkcs5" and pad_len%8 != 0:
    #     raise ValueError("PKCS5 padding错误")
    return data[:-pad_len]

def aes_encrypt(data: bytes, key: bytes, iv: bytes = None, mode: Literal["CBC", "ECB"] = "CBC", padding: Literal["pkcs5", "pkcs7"] = "pkcs7") -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key 长度必须为 16/24/32 字节")
    block_size = AES.block_size
    padded = pkcs_padding(data, block_size, mode=padding)
    if mode == "CBC":
        if iv is None or len(iv) != block_size:
            raise ValueError("CBC模式需要长度为16字节的IV")
        cipher = AES.new(key, AES.MODE_CBC, iv)
    elif mode == "ECB":
        cipher = AES.new(key, AES.MODE_ECB)
    else:
        raise ValueError("不支持的AES模式")
    return cipher.encrypt(padded)

def aes_decrypt(encrypted: bytes, key: bytes, iv: bytes = None, mode: Literal["CBC", "ECB"] = "CBC", padding: Literal["pkcs5", "pkcs7"] = "pkcs7") -> bytes:
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key 长度必须为 16/24/32 字节")
    block_size = AES.block_size
    if mode == "CBC":
        if iv is None or len(iv) != block_size:
            raise ValueError("CBC模式需要长度为16字节的IV")
        cipher = AES.new(key, AES.MODE_CBC, iv)
    elif mode == "ECB":
        cipher = AES.new(key, AES.MODE_ECB)
    else:
        raise ValueError("不支持的AES模式")
    decrypted = cipher.decrypt(encrypted)
    return pkcs_unpadding(decrypted, mode=padding)

# logger = logging.getLogger("aesutil")

# def pkcs5_padding(data: bytes, block_size: int) -> bytes:
#     pad_len = block_size - (len(data) % block_size)
#     return data + bytes([pad_len]) * pad_len

# def pkcs5_unpadding(data: bytes) -> bytes:
#     if not data:
#         raise ValueError("解密错误")
#     pad_len = data[-1]
#     if pad_len <= 0 or pad_len > len(data):
#         raise ValueError("解密错误")
#     return data[:-pad_len]

# def AESBase64Encrypt(origin_data: str, key: str, iv: bytes) -> str:
#     key_b = key.encode()
#     if len(key_b) not in (16, 24, 32):
#         raise ValueError("AES key 长度必须为 16/24/32 字节")
#     cipher = AES.new(key_b, AES.MODE_CBC, iv)
#     padded = pkcs5_padding(origin_data.encode("utf-8"), AES.block_size)
#     encrypted = cipher.encrypt(padded)
#     return base64.b64encode(encrypted).decode('utf-8')

# def AESBase64Decrypt(encrypt_data: str, key: str, iv: bytes) -> str:
#     key_b = key.encode()
#     if len(key_b) not in (16, 24, 32):
#         raise ValueError("AES key 长度必须为 16/24/32 字节")
#     try:
#         raw = base64.b64decode(encrypt_data)
#     except Exception as e:
#         logger.error("AES解密错误: %s", e)
#         raise
#     cipher = AES.new(key_b, AES.MODE_CBC, iv)
#     decrypted = cipher.decrypt(raw)
#     try:
#         unp = pkcs5_unpadding(decrypted)
#     except ValueError as e:
#         logger.error("AES解密错误: %s", e)
#         raise
#     return unp.decode('utf-8', errors='ignore')

# def AesEncrypt(origData: bytes, key: bytes) -> bytes:
#     if len(key) not in (16, 24, 32):
#         raise ValueError("AES key 长度必须为 16/24/32 字节")
#     block_size = AES.block_size
#     iv = key[:block_size]
#     cipher = AES.new(key, AES.MODE_CBC, iv)
#     padded = pkcs5_padding(origData, block_size)
#     return cipher.encrypt(padded)

# def AESEncrypt(data: str, key: str) -> bytes:
#     try:
#         return AesEncrypt(data.encode('utf-8'), key.encode())
#     except Exception as e:
#         logger.error("AES加密错误: %s", e)
#         return b""

# def AesDecrypt(encrypted: bytes, key: bytes) -> bytes:
#     if len(key) not in (16, 24, 32):
#         raise ValueError("AES key 长度必须为 16/24/32 字节")
#     block_size = AES.block_size
#     iv = key[:block_size]
#     cipher = AES.new(key, AES.MODE_CBC, iv)
#     decrypted = cipher.decrypt(encrypted)
#     return pkcs5_unpadding(decrypted)

# def AESDecrypt(data: bytes, key: str) -> bytes:
#     try:
#         return AesDecrypt(data, key.encode())
#     except Exception as e:
#         logger.error("AES解密错误: %s", e)
#         return b""

# def AesEncryptEcb(src: str, key: str) -> bytes:
#     key_b = key.encode()
#     if len(key_b) not in (16, 24, 32):
#         raise ValueError("AES密钥错误")
#     if src == "":
#         logger.error("AES原始数据为空")
#         raise ValueError("AES明文数据为空")
#     cipher = AES.new(key_b, AES.MODE_ECB)
#     content = pkcs5_padding(src.encode('utf-8'), cipher.block_size)
#     return cipher.encrypt(content)

# def AesDecryptEcb(crypted: bytes, key: str) -> str:
#     key_b = key.encode()
#     if len(key_b) not in (16, 24, 32):
#         raise ValueError("AES密钥错误")
#     cipher = AES.new(key_b, AES.MODE_ECB)
#     decrypted = cipher.decrypt(crypted)
#     unp = pkcs5_unpadding(decrypted)
#     return unp.decode('utf-8', errors='ignore')
