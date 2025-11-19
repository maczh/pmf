import sys
import os
# import etcd3
from pathlib import Path
from sqlalchemy import  text
from sqlalchemy.orm import  Session, declarative_base
from fastapi import APIRouter

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from app import app
from models import Result

router = APIRouter(prefix="/api/v1")
application = None

@router.get("/verify_order")
def get_pay_order(cmd_id: str):
    try:
        session: Session = application.client.mysql.get_session()
        try:
            order = session.execute(text('SELECT * FROM bum_batch_file_record where cmd_id = :cmd_id'), {'cmd_id': cmd_id}).first()
            # data = []
            # for row in orders:
            #     data.append(row._asdict())
            # print(order._fields)
            if order is None:
                return Result.success(data=None)
            print(order._mapping)
            return Result.success(data=order._asdict())
        except Exception as e:
            return Result.error(msg=str(e))
        finally:
            session.close()  # 确保关闭session
    except Exception as e:
        return Result.error(msg=str(e))

if __name__ == "__main__":
    application = app.App(config_file="test/kmp.yml")
    application.app.include_router(router)
    application.run()
    
    
    