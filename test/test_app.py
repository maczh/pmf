import sys
import os
# import etcd3
from pathlib import Path
from sqlalchemy import  text
from sqlalchemy.orm import  Session, declarative_base
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from core import app
from models import Result
from middleware.postlog import LoggingMiddleware

router = APIRouter(prefix="/api/v1")

class SendMqttMsgReq(BaseModel):
    topic: str
    msg: str

@router.get("/paychannel")
def get_pay_order(channel_id: str):
    try:
        session: Session = app.app.client.mysql.get_session()
        try:
            channel = session.execute(text('SELECT * FROM pay_channel where channel_id = :channel_id'), {'channel_id': channel_id}).first()
            # data = []
            # for row in orders:
            #     data.append(row._asdict())
            # print(order._fields)
            if channel is None:
                return Result.success(data=None)
            print(channel._mapping)
            return Result.success(data=channel._asdict())
        except Exception as e:
            return Result.error(msg=str(e))
        finally:
            session.close()  # 确保关闭session
    except Exception as e:
        return Result.error(msg=str(e))

@router.get("/rustfs/list")
def get_rustfs_list(prefix: str = ''):
    objs = app.app.client.s3.list_objects(prefix=prefix)
    return Result.success(data=objs)


@router.post("/mqtt/send")
def post_mqtt_msg(req: SendMqttMsgReq):
    app.app.client.mqtt.publish(topic=req.topic, payload=req.msg)
    print(f"send mqtt msg to topic:{req.topic}, msg:{req.msg}")
    return Result.success()

if __name__ == "__main__":
    myapp = app.App(config_file="test/kmp.yml")
    myapp.app.add_middleware(LoggingMiddleware)
    myapp.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    myapp.app.include_router(router)
    app.app = myapp
    myapp.run()
    
    
    