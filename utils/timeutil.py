import datetime
import math
from dateutil import parser

def to_datetime_string(dt: datetime.datetime) -> str:
    """转换为datetime字符串"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def to_date_string(dt: datetime.datetime) -> str:
    """转换为date字符串"""
    return dt.strftime("%Y-%m-%d")

def to_time_string(dt: datetime.datetime) -> str:
    """转换为time字符串"""
    return dt.strftime("%H:%M:%S")

def time_sub_days(t1: datetime.datetime, t2: datetime.datetime) -> int:
    """计算两个时间相差的天数"""
    if t1.tzinfo != t2.tzinfo:
        return -1
        
    delta = t1 - t2
    hours = delta.total_seconds() / 3600
    
    if hours <= 0:
        return -1
        
    if hours < 24:
        return 0 if (t1.year == t2.year and t1.month == t2.month and t1.day == t2.day) else 1
    else:
        days = hours / 24
        return int(days) if days.is_integer() else int(days) + 1

def date_format(dt: datetime.datetime, format_str: str) -> str:
    """自定义日期格式化"""
    mapping = {
        'MMMM': '%B', 'MMM': '%b', 'MM': '%m', 'M': '%-m',
        'dddd': '%A', 'ddd': '%a', 'dd': '%d', 'd': '%-d',
        'yyyy': '%Y', 'yy': '%y',
        'HH': '%H', 'H': '%-H', 'hh': '%I', 'h': '%-I',
        'mm': '%M', 'm': '%-M',
        'ss': '%S', 's': '%-S',
        'tt': '%p', 'ZZZ': '%Z', 'Z': '%z'
    }
    for key, value in mapping.items():
        format_str = format_str.replace(key, value)
    return dt.strftime(format_str)

def convert_date_format(time_str: str, format_str: str) -> str:
    """转换日期字符串格式"""
    try:
        dt = parser.parse(time_str)
        return date_format(dt, format_str)
    except Exception as e:
        print(f"日期转换错误: {e}")
        return ""

def get_now_datetime() -> str:
    """获取当前datetime字符串（CST时区）"""
    cst_tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(cst_tz).strftime("%Y-%m-%d %H:%M:%S")

def week_by_date(dt: datetime.datetime) -> int:
    """获取日期所在年份的周数"""
    year_day = dt.timetuple().tm_yday
    year_first_day = dt.replace(month=1, day=1)
    first_day_weekday = year_first_day.weekday()  # 0是周一，6是周日
    
    first_week_days = 7 - first_day_weekday if first_day_weekday != 0 else 1
    
    if year_day <= first_week_days:
        return 1
    else:
        return (year_day - first_week_days) // 7 + 2