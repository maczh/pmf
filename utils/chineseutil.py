import re
import unicodedata

def sub_chinese_string(s: str, begin: int, length: int) -> str:
    """截取中文字符串"""
    rs = list(s)
    lth = len(rs)
    
    if begin < 0:
        begin = 0
    if begin >= lth:
        return ""
    
    end = begin + length
    if end > lth:
        end = lth
        
    return ''.join(rs[begin:end]) if length >= 0 else ''.join(rs[begin:])

def chinese_length(s: str) -> int:
    """计算中文字符长度"""
    return len(list(s))

def is_chinese(s: str) -> bool:
    """判断是否包含中文字符"""
    for c in s:
        if '\u4e00' <= c <= '\u9fa5':
            return True
    return False

def dbc_to_sbc(s: str) -> str:
    """全角转半角"""
    result = []
    for c in s:
        code = ord(c)
        if code == 12288:  # 全角空格
            result.append(chr(32))
        elif 65281 <= code <= 65374:  # 全角字符
            result.append(chr(code - 65248))
        else:
            result.append(c)
    return ''.join(result)