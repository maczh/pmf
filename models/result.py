from typing import Any, Union, List, Dict
import json

class Result:
    def __init__(self, code: int = 200, msg: str = "success", data: Any = None):
        """
        初始化Result对象
        :param code: 状态码，默认200表示成功
        :param msg: 消息
        :param data: 数据，可以是任意类型
        """
        self.code = code
        self.msg = msg
        self.data = data

    @classmethod
    def success(cls, data: Any = None, msg: str = "success") -> 'Result':
        """
        创建成功响应
        :param data: 响应数据
        :param msg: 成功消息
        :return: Result对象
        """
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def success(cls, data: Any = None,  page_index: int = 1, page_size: int = 10, total: int = 0) -> 'Result':
        """
        创建成功响应
        :param data: 响应数据
        :param msg: 成功消息
        :return: Result对象
        """
        res = cls(code=200, msg="success", data=data)
        res.page = {
            "index" : page_index,
            "size" : page_size,
            "total" : total
        } 
        return res

    @classmethod
    def error(cls, code: int = 400, msg: str = "error", data: Any = None) -> 'Result':
        """
        创建错误响应
        :param code: 错误码
        :param msg: 错误消息
        :param data: 错误详情
        :return: Result对象
        """
        return cls(code=code, msg=msg, data=data)

    def to_json(self) -> str:
        """
        将Result对象转换为JSON字符串
        :return: JSON字符串
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_dict(self) -> Dict:
        """
        将Result对象转换为字典
        :return: 字典
        """
        if hasattr(self, 'page') and self.page['total'] > 0:
            return {
                'code': self.code,
                'msg': self.msg,
                'data': self.data,
                'page': self.page
            }
        else:
            return {
                'code': self.code,
                'msg': self.msg,
                'data': self.data,
            }

    def __str__(self) -> str:
        return self.to_json()

# 使用示例
if __name__ == "__main__":
    # 成功示例 - 返回字典
    success_result = Result.success(data={"name": "张三", "age": 18})
    print(success_result.to_json())
    
    # 成功示例 - 返回列表
    success_result = Result.success(data=[1, 2, 3], page_index=5, page_size=10, total=53)
    print(success_result.to_json())
    
    # 错误示例
    error_result = Result.error(code=404, msg="未找到资源")
    print(error_result.to_json())
