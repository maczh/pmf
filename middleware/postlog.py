import time
import logging
from datetime import datetime
import sys
import os
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core import app

# 配置 logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        start_dt = datetime.utcnow()

        # 请求信息
        request_info = {
            "uri": str(request.url.path),
            "method": request.method,
            "headers": dict(request.headers),
        }
        request_params: dict = {}
        if request.method == "GET":
            request_params = dict(request.query_params)
        elif request.method == "POST":
            if request.headers.get("Content-Type").startswith("application/json"):
                request_params = await request.json()
            elif request.headers.get("Content-Type").startswith("application/x-www-form-urlencoded") or  request.headers.get("Content-Type").startswith("multipart/form-data"):
                request_params = await request.form()
        request_params.update(dict(request.query_params))
        request_info["body"] = request_params
        # 输出日志
        logger.debug(f"{request_info['method']}|接口地址:{request_info['uri']} | 请求参数:{request_params}")

        # 执行请求
        response: Response = await call_next(request)

        # 响应信息
        process_time = (time.time() - start_time) * (10 ^ 6)
        end_dt = datetime.utcnow()

        try:
            # 读取响应体（同样需还原，避免响应异常）
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            # 还原响应体流
            async def async_iter():
                yield response_body
            response.body_iterator = async_iter()
            response_text = response_body.decode("utf-8")
        except Exception:
            response_text = None
        logger.debug(f"{request_info['method']}|接口地址:{request_info['uri']} | 响应参数:{response_text}")

        log_data = {
            "uri": request_info["uri"],
            "method": request_info["method"],
            "headers": request_info["headers"],
            "request_body": request_info["body"],
            "response_body": json.loads(response_text) if response_text else None,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S",start_dt.timetuple()),
            "end_time": time.strftime("%Y-%m-%d %H:%M:%S",end_dt.timetuple()),
            "ttl": process_time,
        }

        # 保存到 MongoDB
        if app.app.client.mgo is not None:
            logger.debug("开始写入mongodb日志")
            app.app.client.mgo.get_collection(app.app.config.pmf.log.req.to_primitive()).insert_one(log_data)

        return response


