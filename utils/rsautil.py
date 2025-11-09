from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
import base64
import hexlib

class RSASecurity:
    def __init__(self):
        self.pub_key = None  # 公钥对象
        self.pri_key = None  # 私钥对象
        
    def set_public_key(self, pub_str: str) -> bool:
        """设置公钥（PEM格式字符串）"""
        try:
            self.pub_key = serialization.load_pem_public_key(pub_str.encode())
            return True
        except Exception:
            return False
            
    def set_private_key(self, pri_str: str) -> bool:
        """设置私钥（PEM格式字符串）"""
        try:
            self.pri_key = serialization.load_pem_private_key(pri_str.encode(), password=None)
            return True
        except Exception:
            return False
            
    def pub_key_encrypt(self, data: bytes) -> bytes:
        """公钥加密"""
        if not self.pub_key:
            raise ValueError("请先设置公钥")
        return self.pub_key.encrypt(
            data,
            padding.PKCS1v15()
        )
        
    def pri_key_decrypt(self, data: bytes) -> bytes:
        """私钥解密"""
        if not self.pri_key:
            raise ValueError("请先设置私钥")
        return self.pri_key.decrypt(
            data,
            padding.PKCS1v15()
        )
        
    def sign_sha1_with_rsa(self, data: str) -> str:
        """使用SHA1withRSA签名"""
        if not self.pri_key:
            raise ValueError("请先设置私钥")
        signature = self.pri_key.sign(
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return base64.b64encode(signature).decode()
        
    def verify_sha256_with_rsa(self, data: str, sign_data: str) -> bool:
        """使用SHA256withRSA验证签名"""
        if not self.pub_key:
            raise ValueError("请先设置公钥")
        try:
            self.pub_key.verify(
                base64.b64decode(sign_data),
                data.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False