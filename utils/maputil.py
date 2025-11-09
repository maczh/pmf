import json
from typing import Any, Dict, List, Tuple

def map_ito_s(src: Dict[str, Any]) -> Dict[str, str]:
    """将any类型value的map转换为string类型value的map"""
    return {k: str(v) for k, v in src.items()}

def map_stoi(src: Dict[str, str]) -> Dict[str, Any]:
    """将string类型value的map转换为any类型value的map"""
    return {k: v for k, v in src.items()}

def exists(src: Dict[str, str], key: str) -> bool:
    """检查string map中是否存在key"""
    return key in src

def existi(src: Dict[str, Any], key: str) -> bool:
    """检查any map中是否存在key"""
    return key in src

def sort_map_by_value(src: Dict[str, Any]) -> List[Tuple[str, Any]]:
    """按值排序map"""
    return sorted(src.items(), key=lambda x: x[1])

def sort_map_by_value_desc(src: Dict[str, Any]) -> List[Tuple[str, Any]]:
    """按值降序排序map"""
    return sorted(src.items(), key=lambda x: x[1], reverse=True)

def map_get(input_data: Any, field_name: str) -> Any:
    """获取map中的字段，支持嵌套（field.subfield）"""
    fields = field_name.split('.')
    result = input_data
    
    for field in fields:
        if isinstance(result, dict):
            if field in result:
                result = result[field]
            else:
                return None
        else:
            return None
    return result