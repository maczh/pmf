from typing import Tuple, Optional


def utf8_to_gbk(utf8_str: str) -> str:
    """UTF-8字符串转GBK字符串"""
    try:
        return utf8_str.encode('utf-8').decode('utf-8').encode('gbk').decode('gbk')
    except UnicodeEncodeError:
        return utf8_str


def gbk_to_utf8(gbk_str: str) -> Tuple[str, Optional[Exception]]:
    """GBK字符串转UTF-8字符串"""
    try:
        # 先将字符串按GBK编码为字节，再解码为UTF-8
        gbk_bytes = gbk_str.encode('latin-1')  # 保留原始字节
        utf8_str = gbk_bytes.decode('gbk')
        return utf8_str, None
    except UnicodeDecodeError as e:
        return "", e


def clear_utf8_bom(bom_str: str) -> str:
    """清除UTF-8字符串的BOM头"""
    bom_bytes = bom_str.encode('utf-8')
    # UTF-8 BOM为0xefbbbf
    if len(bom_bytes) >= 3 and bom_bytes[:3] == b'\xef\xbb\xbf':
        # 去除BOM后转字符串并替换回车
        return bom_bytes[3:].decode('utf-8').replace('\r', '')
    return bom_str