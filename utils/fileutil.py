import os
import pathlib
import shutil

def self_path() -> str:
    """获取当前执行文件路径"""
    return os.path.abspath(__file__)

def self_dir() -> str:
    """获取当前执行文件目录"""
    return os.path.dirname(self_path())

def basename(file_path: str) -> str:
    """获取文件名"""
    return os.path.basename(file_path)

def dirname(file_path: str) -> str:
    """获取目录名"""
    return os.path.dirname(file_path)

def insure_dir(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def ext(file_path: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(file_path)[1]

def rename(old_path: str, new_path: str) -> None:
    """重命名文件"""
    os.rename(old_path, new_path)

def unlink(file_path: str) -> None:
    """删除文件"""
    os.remove(file_path)

def is_file(file_path: str) -> bool:
    """判断是否为文件"""
    return os.path.isfile(file_path)

def is_exist(path: str) -> bool:
    """判断路径是否存在"""
    return os.path.exists(path)

def is_dir(path: str) -> bool:
    """判断是否为目录"""
    return os.path.isdir(path)

def read_file_to_bytes(file_path: str) -> bytes:
    """读取文件为字节流"""
    with open(file_path, 'rb') as f:
        return f.read()

def read_file_to_string(file_path: str, encoding: str = 'utf-8') -> str:
    """读取文件为字符串"""
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()

def write_bytes_to_file(file_path: str, data: bytes) -> int:
    """写入字节流到文件"""
    insure_dir(os.path.dirname(file_path))
    with open(file_path, 'wb') as f:
        return f.write(data)

def write_string_to_file(file_path: str, data: str, encoding: str = 'utf-8') -> int:
    """写入字符串到文件"""
    return write_bytes_to_file(file_path, data.encode(encoding))

def dirs_under(dir_path: str) -> list[str]:
    """获取目录下的所有子目录"""
    if not is_exist(dir_path):
        return []
    return [f for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]

def files_under(dir_path: str) -> list[str]:
    """获取目录下的所有文件"""
    if not is_exist(dir_path):
        return []
    return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]