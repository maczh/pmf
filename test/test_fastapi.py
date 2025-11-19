import sys
import os
import fastapi
import uvicorn

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from models.result import Result
from test_mysql import PayChannel
from db.mysqlClient import mysql
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import  sessionmaker, Session, declarative_base

from sqlalchemy import (
    Column, BigInteger, String, DateTime, text
)


# 测试FastAPI
app = fastapi.FastAPI()

@app.get("/channel")
def read_root():
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
    return Result.success(data=channels).to_dict()
# 测试Result类
#  result = Result.success(data={"name": "John", "age": 30})
#  print(result.to_dict())  # 输出: {'code': 200, 'msg': 'success', 'data': {'name': 'John', 'age': 30}}
#  print(result.to_json())  # 输出: {"code":200,"msg":"success","data":{"name":"John","age":30}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)