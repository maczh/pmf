import sys
import os
import fastapi

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from models.result import Result

# 测试FastAPI
app = fastapi.FastAPI()

@app.get("/user")
def read_root():
    return Result.success(data={"name": "John", "age": 30}).to_dict()
# 测试Result类
#  result = Result.success(data={"name": "John", "age": 30})
#  print(result.to_dict())  # 输出: {'code': 200, 'msg': 'success', 'data': {'name': 'John', 'age': 30}}
#  print(result.to_json())  # 输出: {"code":200,"msg":"success","data":{"name":"John","age":30}}