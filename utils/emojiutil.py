import re
import json

def unicode_emoji_decode(s: str) -> str:
    """Emoji表情解码（将\\u形式转为实际表情）"""
    # 匹配[\uXXXX]格式的表情
    pattern = re.compile(r'\[\\u[0-9a-zA-Z]+\]')
    emoji_list = pattern.findall(s)
    
    for emoji in emoji_list:
        # 提取Unicode编码
        code = re.sub(r'\[|\\u|\]', '', emoji)
        try:
            # 转换为字符
            char = chr(int(code, 16))
            s = s.replace(emoji, char)
        except ValueError:
            continue
    return s

def unicode_emoji_code(s: str) -> str:
    """将Emoji转为\\u形式编码"""
    result = []
    for char in s:
        # Emoji通常是4字节字符
        if len(char.encode('utf-8')) == 4:
            code = hex(ord(char))[2:]  # 去除0x前缀
            result.append(f'[\\u{code}]')
        else:
            result.append(char)
    return ''.join(result)

def trim_emoji(s: str) -> str:
    """清除字符串中的Emoji表情"""
    result = []
    for char in s:
        # 保留非4字节字符（非Emoji）
        if len(char.encode('utf-8')) != 4:
            result.append(char)
    return ''.join(result)