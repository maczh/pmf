from typing import List, Any, Union


def string_array_contains(src: List[str], dst: str) -> bool:
    """判断字符串列表是否包含目标字符串"""
    return dst in src


def string_array_delete(src: List[str], index: int) -> List[str]:
    """删除字符串列表中指定索引的元素"""
    if 0 <= index < len(src):
        return src[:index] + src[index+1:]
    return src.copy()


def int_array_contains(src: List[int], dst: int) -> bool:
    """判断整数列表是否包含目标整数"""
    return dst in src


def int_array_delete(src: List[int], index: int) -> List[int]:
    """删除整数列表中指定索引的元素"""
    if 0 <= index < len(src):
        return src[:index] + src[index+1:]
    return src.copy()


def float64_array_contains(src: List[float], dst: float) -> bool:
    """判断浮点数列表是否包含目标浮点数"""
    return dst in src


def float64_array_delete(src: List[float], index: int) -> List[float]:
    """删除浮点数列表中指定索引的元素"""
    if 0 <= index < len(src):
        return src[:index] + src[index+1:]
    return src.copy()


def slice_contains(sl: List[Any], v: Any) -> bool:
    """判断任意类型列表是否包含目标元素"""
    return v in sl


def slice_merge(slice1: List[Any], slice2: List[Any]) -> List[Any]:
    """合并两个任意类型列表"""
    return slice1 + slice2


def slice_merge_int(slice1: List[int], slice2: List[int]) -> List[int]:
    """合并两个整数列表"""
    return slice1 + slice2


def slice_unique_int(s: List[int]) -> List[int]:
    """整数列表去重"""
    return list(set(s))


def slice_unique_int64(s: List[int]) -> List[int]:
    """int64列表去重（Python中int兼容int64）"""
    return list(set(s))


def slice_unique_string(s: List[str]) -> List[str]:
    """字符串列表去重"""
    return list(set(s))


def slice_sum_int(intslice: List[int]) -> int:
    """整数列表求和"""
    return sum(intslice)


def slice_sum_int64(intslice: List[int]) -> int:
    """int64列表求和"""
    return sum(intslice)


def slice_sum_float64(floatslice: List[float]) -> float:
    """浮点数列表求和"""
    return sum(floatslice)


def array_str_to_int(data: List[str]) -> List[int]:
    """字符串列表转整数列表（忽略转换失败的元素）"""
    result = []
    for s in data:
        try:
            result.append(int(s))
        except ValueError:
            continue
    return result


def array_int_to_str(data: List[int]) -> List[str]:
    """整数列表转字符串列表"""
    return [str(x) for x in data]


def trim_space_str_in_array(s: str, data: List[str]) -> bool:
    """判断字符串是否存在于列表中（忽略列表元素的前后空格）"""
    s_trimmed = s.strip()
    for item in data:
        if s_trimmed == item.strip():
            return True
    return False


def un_split_string(src: List[str], sep: str) -> str:
    """用分隔符拼接字符串列表"""
    return sep.join(src)


def union_string_slice(slice1: List[str], slice2: List[str]) -> List[str]:
    """求两个字符串列表的并集"""
    return list(set(slice1) | set(slice2))


def intersect_string_slice(slice1: List[str], slice2: List[str]) -> List[str]:
    """求两个字符串列表的交集"""
    return list(set(slice1) & set(slice2))


def difference_string_slice(slice1: List[str], slice2: List[str]) -> List[str]:
    """求两个字符串列表的差集（slice1 - 交集）"""
    return list(set(slice1) - set(slice2))