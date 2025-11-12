import os
import shutil
import subprocess
from typing import List, Optional, Union

class GlusterFSManager:
    """
    GlusterFS 管理类，提供文件系统操作的基本方法
    """
    
    def __init__(self, mount_point: str = "/mnt/glusterfs"):
        """
        初始化 GlusterFS 管理器
        
        :param mount_point: GlusterFS 挂载点路径，默认为 /mnt/glusterfs
        """
        self.mount_point = mount_point
        self._ensure_mount_point()
    
    def _ensure_mount_point(self) -> None:
        """确保挂载点存在且可访问"""
        if not os.path.exists(self.mount_point):
            raise FileNotFoundError(f"GlusterFS 挂载点 {self.mount_point} 不存在")
        if not os.path.ismount(self.mount_point):
            raise RuntimeError(f"{self.mount_point} 不是有效的 GlusterFS 挂载点")
    
    def _get_full_path(self, path: str) -> str:
        """获取完整的文件系统路径"""
        return os.path.join(self.mount_point, path.lstrip('/'))
    
    def upload_file(self, local_path: str, remote_path: str, overwrite: bool = False) -> bool:
        """
        上传文件到 GlusterFS
        
        :param local_path: 本地文件路径
        :param remote_path: GlusterFS 上的目标路径
        :param overwrite: 是否覆盖已存在的文件
        :return: 操作是否成功
        """
        try:
            full_remote_path = self._get_full_path(remote_path)
            
            # 检查目标文件是否存在
            if os.path.exists(full_remote_path) and not overwrite:
                raise FileExistsError(f"目标文件 {remote_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(full_remote_path), exist_ok=True)
            
            # 复制文件
            shutil.copy2(local_path, full_remote_path)
            return True
        except Exception as e:
            print(f"上传文件失败: {str(e)}")
            return False
    
    def download_file(self, remote_path: str, local_path: str, overwrite: bool = False) -> bool:
        """
        从 GlusterFS 下载文件
        
        :param remote_path: GlusterFS 上的文件路径
        :param local_path: 本地目标路径
        :param overwrite: 是否覆盖已存在的文件
        :return: 操作是否成功
        """
        try:
            full_remote_path = self._get_full_path(remote_path)
            
            # 检查源文件是否存在
            if not os.path.exists(full_remote_path):
                raise FileNotFoundError(f"源文件 {remote_path} 不存在")
            
            # 检查目标文件是否存在
            if os.path.exists(local_path) and not overwrite:
                raise FileExistsError(f"目标文件 {local_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 复制文件
            shutil.copy2(full_remote_path, local_path)
            return True
        except Exception as e:
            print(f"下载文件失败: {str(e)}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """
        删除 GlusterFS 上的文件或目录
        
        :param path: 要删除的文件或目录路径
        :return: 操作是否成功
        """
        try:
            full_path = self._get_full_path(path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"文件或目录 {path} 不存在")
            
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return True
        except Exception as e:
            print(f"删除失败: {str(e)}")
            return False
    
    def move_file(self, src_path: str, dst_path: str, overwrite: bool = False) -> bool:
        """
        移动/重命名 GlusterFS 上的文件或目录
        
        :param src_path: 源路径
        :param dst_path: 目标路径
        :param overwrite: 是否覆盖已存在的目标
        :return: 操作是否成功
        """
        try:
            full_src_path = self._get_full_path(src_path)
            full_dst_path = self._get_full_path(dst_path)
            
            if not os.path.exists(full_src_path):
                raise FileNotFoundError(f"源文件或目录 {src_path} 不存在")
            
            if os.path.exists(full_dst_path) and not overwrite:
                raise FileExistsError(f"目标文件或目录 {dst_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(full_dst_path), exist_ok=True)
            
            # 移动文件
            shutil.move(full_src_path, full_dst_path)
            return True
        except Exception as e:
            print(f"移动失败: {str(e)}")
            return False
    
    def copy_file(self, src_path: str, dst_path: str, overwrite: bool = False) -> bool:
        """
        复制 GlusterFS 上的文件或目录
        
        :param src_path: 源路径
        :param dst_path: 目标路径
        :param overwrite: 是否覆盖已存在的目标
        :return: 操作是否成功
        """
        try:
            full_src_path = self._get_full_path(src_path)
            full_dst_path = self._get_full_path(dst_path)
            
            if not os.path.exists(full_src_path):
                raise FileNotFoundError(f"源文件或目录 {src_path} 不存在")
            
            if os.path.exists(full_dst_path) and not overwrite:
                raise FileExistsError(f"目标文件或目录 {dst_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(full_dst_path), exist_ok=True)
            
            # 复制文件或目录
            if os.path.isdir(full_src_path):
                shutil.copytree(full_src_path, full_dst_path)
            else:
                shutil.copy2(full_src_path, full_dst_path)
            return True
        except Exception as e:
            print(f"复制失败: {str(e)}")
            return False
    
    def list_directory(self, path: str = "/", recursive: bool = False) -> List[str]:
        """
        列出目录内容
        
        :param path: 目录路径，默认为根目录
        :param recursive: 是否递归列出子目录
        :return: 文件和目录列表
        """
        try:
            full_path = self._get_full_path(path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"目录 {path} 不存在")
            
            if not os.path.isdir(full_path):
                raise NotADirectoryError(f"{path} 不是目录")
            
            if recursive:
                result = []
                for root, dirs, files in os.walk(full_path):
                    for name in dirs + files:
                        rel_path = os.path.relpath(os.path.join(root, name), self.mount_point)
                        result.append(rel_path)
                return result
            else:
                return [os.path.relpath(os.path.join(full_path, name), self.mount_point) 
                        for name in os.listdir(full_path)]
        except Exception as e:
            print(f"列出目录失败: {str(e)}")
            return []
    
    def file_exists(self, path: str) -> bool:
        """
        检查文件或目录是否存在
        
        :param path: 文件或目录路径
        :return: 是否存在
        """
        try:
            full_path = self._get_full_path(path)
            return os.path.exists(full_path)
        except Exception:
            return False
    
    def get_file_info(self, path: str) -> Optional[dict]:
        """
        获取文件或目录信息
        
        :param path: 文件或目录路径
        :return: 包含文件信息的字典，如果文件不存在则返回 None
        """
        try:
            full_path = self._get_full_path(path)
            if not os.path.exists(full_path):
                return None
            
            stat = os.stat(full_path)
            return {
                'path': path,
                'size': stat.st_size,
                'is_dir': os.path.isdir(full_path),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'accessed_time': stat.st_atime,
                'mode': stat.st_mode
            }
        except Exception as e:
            print(f"获取文件信息失败: {str(e)}")
            return None
    
    def create_directory(self, path: str, mode: int = 0o755) -> bool:
        """
        创建目录
        
        :param path: 目录路径
        :param mode: 目录权限模式
        :return: 操作是否成功
        """
        try:
            full_path = self._get_full_path(path)
            os.makedirs(full_path, mode=mode, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {str(e)}")
            return False
    
    def get_disk_usage(self) -> dict:
        """
        获取磁盘使用情况
        
        :return: 包含磁盘使用信息的字典
        """
        try:
            stat = shutil.disk_usage(self.mount_point)
            return {
                'total': stat.total,
                'used': stat.used,
                'free': stat.free,
                'mount_point': self.mount_point
            }
        except Exception as e:
            print(f"获取磁盘使用情况失败: {str(e)}")
            return {}
