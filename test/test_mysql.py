# from ..db import mysqlClient
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from db.mysqlClient import mysql

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import  sessionmaker, Session, declarative_base

from sqlalchemy import (
    Column, BigInteger, String, DateTime, text
)
# BaseModel = declarative_base()

class PayChannel(declarative_base()):
    __tablename__ = "pay_channel"
    __table_args__ = {"schema": "jihai"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    channel_id = Column(String(64), nullable=False, unique=True, server_default=text("''"), comment="渠道ID")
    channel_name = Column(String(64), nullable=False, server_default=text("''"), comment="渠道名称")
    service_name = Column(String(64), nullable=False, server_default=text("''"), comment="支付通道服务名称")
    pay_uri = Column(String(255), nullable=True, server_default=text("''"), comment="支付通道支付接口URI")
    refund_uri = Column(String(255), nullable=True, server_default=text("''"), comment="支付通道退款接口URI")
    cancel_uri = Column(String(255), nullable=True, server_default=text("''"), comment="支付通道取消接口URI")
    query_uri = Column(String(255), nullable=True, server_default=text("''"), comment="支付通道查询接口URI")
    type = Column(String(20), nullable=False, comment="通道类型")
    create_time = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    update_time = Column(
        DateTime,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        comment="更新时间",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "service_name": self.service_name,
            "pay_uri": self.pay_uri,
            "refund_uri": self.refund_uri,
            "cancel_uri": self.cancel_uri,
            "query_uri": self.query_uri,
            "type": self.type,
            "create_time": self.create_time,
            "update_time": self.update_time,
        }

if __name__ == "__main__":
    # 示例用法
    mysql_client = mysql(
        uri="mysql+pymysql://jihai:Voodoo#123456@localhost:3306/jihai",
        pool_size=5,
        max_overflow=10,
        debug=True,
    )
   
    # 获取会话
    session: Session = mysql_client.get_session()

    # 查询示例
    channels: List[PayChannel] = session.query(PayChannel).all()
    for channel in channels:
        print(channel.to_dict())

    # 关闭会话
    session.close()