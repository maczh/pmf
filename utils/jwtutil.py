import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

class JWTUtil:
    def __init__(self, secret: str):
        self.secret = secret
        
    def generate_token(self, claims: Dict, expires_hours: int = 24) -> str:
        """
        生成JWT令牌
        :param claims: 自定义声明
        :param expires_hours: 过期时间（小时）
        """
        # 设置过期时间
        exp = datetime.utcnow() + timedelta(hours=expires_hours)
        claims['exp'] = exp
        # 使用HS256算法签名
        return jwt.encode(claims, self.secret, algorithm='HS256')
        
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        验证JWT令牌
        :return: 解码后的声明（验证失败返回None）
        """
        try:
            return jwt.decode(token, self.secret, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None