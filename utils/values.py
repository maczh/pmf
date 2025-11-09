from typing import Any, Optional


def get_default(value: Any, default: Any) -> Any:
    """获取值，若值为空则返回默认值"""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    return value


def is_null(value: Any) -> bool:
    """判断值是否为空（None、空字符串、空列表等）"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, tuple, dict, set)) and len(value) == 0:
        return True
    return False


def to_int(value: Any, default: int = 0) -> int:
    """将值转换为整数，失败则返回默认值"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """将值转换为浮点数，失败则返回默认值"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def to_bool(value: Any, default: bool = False) -> bool:
    """将值转换为布尔值，失败则返回默认值"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower_val = value.lower()
        if lower_val in ("true", "1", "yes"):
            return True
        if lower_val in ("false", "0", "no"):
            return False
    if isinstance(value, (int, float)):
        return value != 0
    return default