import re
from typing import Tuple


# 正则表达式模式
CHINA_MOBILE_PATTERN = r'^1[0-9]{10}$'
NICKNAME_PATTERN = r'^[a-z0-9A-Z\u4e00-\u9fa5]+(_[a-z0-9A-Z\u4e00-\u9fa5]+)*?$'
USERNAME_PATTERN = r'^[a-zA-Z][a-z0-9A-Z]*(_[a-z0-9A-Z]+)*?$'
MAIL_PATTERN = r'^[a-z0-9A-Z]+([_\-\.][a-z0-9A-Z]+)*?@[a-z0-9A-Z]+([\-\.][a-z0-9A-Z]+)*?\.[a-zA-Z]{2,}$'
CHINESE_NAME_PATTERN = r'^\u4e00-\u9fa5+(\u00B7\u4e00-\u9fa5+)*?$'
CHINESE_NAME_EX_PATTERN = r'^\u4e00-\u9fa5+([\u00B7\u2022\u2027\u30FB\u002E\u0387\u16EB\u2219\u22C5\uFF65\u05BC]\u4e00-\u9fa5+)*?$'
ID_CARD_PATTERN = r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)'


def is_china_mobile(s: str) -> bool:
    """验证是否为中国大陆手机号"""
    return len(s) == 11 and re.match(CHINA_MOBILE_PATTERN, s) is not None


def is_nickname(s: str) -> bool:
    """验证是否为合法昵称（字母、数字、汉字、下划线，下划线不连续）"""
    return len(s) > 0 and re.match(NICKNAME_PATTERN, s) is not None


def is_username(s: str) -> bool:
    """验证是否为合法用户名（字母开头，允许数字和下划线，下划线不连续）"""
    return len(s) > 0 and re.match(USERNAME_PATTERN, s) is not None


def is_mail(s: str) -> bool:
    """验证是否为合法邮箱地址"""
    return len(s) >= 6 and re.match(MAIL_PATTERN, s) is not None


def is_chinese_name(s: str) -> bool:
    """验证是否为合法中文姓名（支持·分隔）"""
    return re.match(CHINESE_NAME_PATTERN, s) is not None


def is_chinese_name_ex(s: str) -> Tuple[str, bool]:
    """
    验证中文姓名（支持多种间隔符并自动修正为·）
    :return: (修正后的姓名, 是否合法)
    """
    if is_chinese_name(s):
        return s, True
    if not re.match(CHINESE_NAME_EX_PATTERN, s):
        return s, False
    
    # 替换间隔符为·
    separators = {'\u2022', '\u2027', '\u30FB', '\u002E', '\u0387', '\u16EB', '\u2219', '\u22C5', '\uFF65', '\u05BC'}
    corrected = []
    for c in s:
        if c in separators:
            corrected.append('\u00B7')
        else:
            corrected.append(c)
    corrected_str = ''.join(corrected)
    return corrected_str, True


def is_id_card(card_no: str) -> bool:
    """验证是否为15位或18位身份证号"""
    return re.match(ID_CARD_PATTERN, card_no) is not None