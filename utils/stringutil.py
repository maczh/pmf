import string
import random
from typing import List


def is_empty(s: str) -> bool:
    """判断字符串是否为空（包括仅含空白字符）"""
    return s.strip() == ""


def trim(s: str) -> str:
    """去除字符串前后空白"""
    return s.strip()


def left(s: str, length: int) -> str:
    """获取字符串左侧指定长度的子串"""
    return s[:length] if len(s) >= length else s


def right(s: str, length: int) -> str:
    """获取字符串右侧指定长度的子串"""
    return s[-length:] if len(s) >= length else s


def substring(s: str, start: int, end: int) -> str:
    """获取字符串的子串（支持负索引）"""
    return s[start:end]


def replace_all(s: str, old: str, new: str) -> str:
    """替换字符串中所有匹配的子串"""
    return s.replace(old, new)


def split(s: str, sep: str) -> List[str]:
    """分割字符串"""
    return s.split(sep)


def join(str_list: List[str], sep: str) -> str:
    """拼接字符串列表"""
    return sep.join(str_list)


def random_string(length: int) -> str:
    """生成随机字符串（包含大小写字母和数字）"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def count_occurrences(s: str, substr: str) -> int:
    """统计子串在字符串中出现的次数"""
    return s.count(substr)