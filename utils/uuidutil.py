import uuid
import re

UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)

def is_valid_uuid(uuid_str: str) -> bool:
    """验证UUID格式"""
    return UUID_PATTERN.match(uuid_str) is not None

def new_uuid() -> str:
    """生成新的UUID"""
    return str(uuid.uuid4())

def simple_uuid() -> str:
    """生成不带分隔符的UUID"""
    return new_uuid().replace('-', '')