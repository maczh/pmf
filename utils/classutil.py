import json
from typing import Any, Dict, List, Type, TypeVar

T = TypeVar('T')

def clone(src: Any, dst: Any) -> None:
    """克隆对象"""
    json_str = json.dumps(src, default=lambda o: o.__dict__)
    data = json.loads(json_str)
    for k, v in data.items():
        if hasattr(dst, k):
            setattr(dst, k, v)

def class2map(obj: Any) -> Dict[str, Any]:
    """将对象转换为map"""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def class2map_string(obj: Any) -> Dict[str, str]:
    """将对象转换为string value的map"""
    result = {}
    obj_map = class2map(obj)
    for k, v in obj_map.items():
        if isinstance(v, (dict, list, tuple)):
            result[k] = json.dumps(v)
        else:
            result[k] = str(v)
    return result

def get_class_fields(obj: Any) -> List[str]:
    """获取对象的字段名"""
    return [field for field in dir(obj) if not field.startswith('__')]

def any_to_map(obj: Any) -> Dict[str, str]:
    """将任意类型转换为string map"""
    if obj is None:
        return {}
    
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if isinstance(v, (dict, list, tuple)):
                result[k] = json.dumps(v)
            else:
                result[k] = str(v)
        return result
        
    if hasattr(obj, '__dict__'):
        return class2map_string(obj)
        
    return {}

def copy_class(src: Any, dst: Any) -> None:
    """复制结构体字段"""
    src_map = class2map(src)
    for k, v in src_map.items():
        if hasattr(dst, k):
            setattr(dst, k, v)

def deep_copy(src: Any) -> Any:
    """深拷贝对象"""
    return json.loads(json.dumps(src, default=lambda o: o.__dict__))