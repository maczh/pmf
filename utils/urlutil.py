import urllib.parse

def url_encode(raw_string: str) -> str:
    """URL编码"""
    return urllib.parse.quote(raw_string)

def url_decode(encoded: str) -> str:
    """URL解码"""
    return urllib.parse.unquote(encoded)