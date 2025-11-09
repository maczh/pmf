import re
from typing import Tuple


def is_safe_sql(sql: str) -> Tuple[bool, str]:
    """
    检查SQL是否存在注入风险
    :return: (是否安全, 风险原因)
    """
    # 危险关键字（SQL注入常见特征）
    dangerous_patterns = [
        r"union\s+all", r"union\s+select",  # UNION查询注入
        r"insert\s+into", r"update\s+.+set", r"delete\s+from",  # 写操作注入
        r"drop\s+table", r"truncate\s+table",  # 破坏操作
        r"exec\s*\(", r"execute\s*\(",  # 执行命令
        r"xp_cmdshell",  # 系统命令执行
        r"--", r"\#", r";",  # 注释或多语句分隔
        r"or\s+1=1", r"and\s+1=1",  # 条件注入
        r"sleep\(\d+\)", r"benchmark\(",  # 时间盲注
    ]
    
    # 忽略大小写检查
    for pattern in dangerous_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            return False, f"包含危险SQL片段: {pattern}"
    
    # 检查单引号未转义（简单判断）
    if "'" in sql and "''" not in sql:
        return False, "可能存在未转义的单引号注入风险"
    
    return True, "安全"