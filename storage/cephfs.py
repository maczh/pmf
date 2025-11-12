import os
import shutil
import rados
import cephfs
from typing import List, Optional, Union, Dict, Any

class CephFileManager:
    """
    Ceph 文件管理类，提供与 Ceph 集群交互的基本方法
    """
    
    def __init__(self, ceph_conf: str = "/etc/ceph/ceph.conf", 
                 client_id: str = "admin", 
                 pool_name: str = "data",
                 fs_name: str = "cephfs"):
        """
        初始化 Ceph 文件管理器
        
        :param ceph_conf: Ceph 配置文件路径
        :param client_id: Ceph 客户端 ID
        :param pool_name: RADOS 存储池名称
        :param fs_name: CephFS 文件系统名称
        """
        self.ceph_conf = ceph_conf
        self.client_id = client_id
        self.pool_name = pool_name
        self.fs_name = fs_name
        
        # 初始化 RADOS 连接
        self.rados_cluster = None
        self.rados_ioctx = None
        
        # 初始化 CephFS 连接
        self.cephfs_mount = None
        
        self._connect()
    
    def _connect(self) -> None:
        """建立与 Ceph 集群的连接"""
        try:
            # 连接 RADOS
            self.rados_cluster = rados.Rados(conffile=self.ceph_conf, 
                                            rados_id=self.client_id)
            self.rados_cluster.connect()
            self.rados_ioctx = self.rados_cluster.open_ioctx(self.pool_name)
            
            # 连接 CephFS
            self.cephfs_mount = cephfs.CephMount()
            self.cephfs_mount.mount()
        except Exception as e:
            self._cleanup()
            raise ConnectionError(f"连接 Ceph 集群失败: {str(e)}")
    
    def _cleanup(self) -> None:
        """清理资源"""
        try:
            if self.rados_ioctx:
                self.rados_ioctx.close()
            if self.rados_cluster:
                self.rados_cluster.shutdown()
            if self.cephfs_mount:
                self.cephfs_mount.unmount()
                self.cephfs_mount.release()
        except Exception:
            pass
        
        self.rados_cluster = None
        self.rados_ioctx = None
        self.cephfs_mount = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
    
    def upload_file(self, local_path: str, remote_path: str, 
                   overwrite: bool = False) -> bool:
        """
        上传文件到 CephFS
        
        :param local_path: 本地文件路径
        :param remote_path: CephFS 上的目标路径
        :param overwrite: 是否覆盖已存在的文件
        :return: 操作是否成功
        """
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"本地文件 {local_path} 不存在")
            
            # 检查目标文件是否存在
            if self.file_exists(remote_path) and not overwrite:
                raise FileExistsError(f"目标文件 {remote_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            remote_dir = os.path.dirname(remote_path)
            if remote_dir and not self.file_exists(remote_dir):
                self.create_directory(remote_dir)
            
            # 读取本地文件并写入 CephFS
            with open(local_path, 'rb') as local_file:
                with self.cephfs_mount.open(remote_path, 'w', mode=0o644) as remote_file:
                    shutil.copyfileobj(local_file, remote_file)
            
            return True
        except Exception as e:
            print(f"上传文件失败: {str(e)}")
            return False
    
    def download_file(self, remote_path: str, local_path: str, 
                     overwrite: bool = False) -> bool:
        """
        从 CephFS 下载文件
        
        :param remote_path: CephFS 上的文件路径
        :param local_path: 本地目标路径
        :param overwrite: 是否覆盖已存在的文件
        :return: 操作是否成功
        """
        try:
            # 检查源文件是否存在
            if not self.file_exists(remote_path):
                raise FileNotFoundError(f"源文件 {remote_path} 不存在")
            
            # 检查目标文件是否存在
            if os.path.exists(local_path) and not overwrite:
                raise FileExistsError(f"目标文件 {local_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 从 CephFS 读取文件并写入本地
            with self.cephfs_mount.open(remote_path, 'r') as remote_file:
                with open(local_path, 'wb') as local_file:
                    shutil.copyfileobj(remote_file, local_file)
            
            return True
        except Exception as e:
            print(f"下载文件失败: {str(e)}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """
        删除 CephFS 上的文件或目录
        
        :param path: 要删除的文件或目录路径
        :return: 操作是否成功
        """
        try:
            if not self.file_exists(path):
                raise FileNotFoundError(f"文件或目录 {path} 不存在")
            
            if self.is_directory(path):
                self._delete_directory_recursive(path)
            else:
                self.cephfs_mount.unlink(path)
            
            return True
        except Exception as e:
            print(f"删除失败: {str(e)}")
            return False
    
    def _delete_directory_recursive(self, path: str) -> None:
        """递归删除目录及其内容"""
        for entry in self.list_directory(path):
            full_path = os.path.join(path, entry)
            if self.is_directory(full_path):
                self._delete_directory_recursive(full_path)
            else:
                self.cephfs_mount.unlink(full_path)
        self.cephfs_mount.rmdir(path)
    
    def move_file(self, src_path: str, dst_path: str, 
                 overwrite: bool = False) -> bool:
        """
        移动/重命名 CephFS 上的文件或目录
        
        :param src_path: 源路径
        :param dst_path: 目标路径
        :param overwrite: 是否覆盖已存在的目标
        :return: 操作是否成功
        """
        try:
            if not self.file_exists(src_path):
                raise FileNotFoundError(f"源文件或目录 {src_path} 不存在")
            
            if self.file_exists(dst_path) and not overwrite:
                raise FileExistsError(f"目标文件或目录 {dst_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst_path)
            if dst_dir and not self.file_exists(dst_dir):
                self.create_directory(dst_dir)
            
            # 移动文件或目录
            self.cephfs_mount.rename(src_path, dst_path)
            return True
        except Exception as e:
            print(f"移动失败: {str(e)}")
            return False
    
    def copy_file(self, src_path: str, dst_path: str, 
                 overwrite: bool = False) -> bool:
        """
        复制 CephFS 上的文件或目录
        
        :param src_path: 源路径
        :param dst_path: 目标路径
        :param overwrite: 是否覆盖已存在的目标
        :return: 操作是否成功
        """
        try:
            if not self.file_exists(src_path):
                raise FileNotFoundError(f"源文件或目录 {src_path} 不存在")
            
            if self.file_exists(dst_path) and not overwrite:
                raise FileExistsError(f"目标文件或目录 {dst_path} 已存在且不允许覆盖")
            
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst_path)
            if dst_dir and not self.file_exists(dst_dir):
                self.create_directory(dst_dir)
            
            if self.is_directory(src_path):
                self._copy_directory_recursive(src_path, dst_path)
            else:
                with self.cephfs_mount.open(src_path, 'r') as src_file:
                    with self.cephfs_mount.open(dst_path, 'w', mode=0o644) as dst_file:
                        shutil.copyfileobj(src_file, dst_file)
            
            return True
        except Exception as e:
            print(f"复制失败: {str(e)}")
            return False
    
    def _copy_directory_recursive(self, src_path: str, dst_path: str) -> None:
        """递归复制目录及其内容"""
        self.create_directory(dst_path)
        for entry in self.list_directory(src_path):
            src_full_path = os.path.join(src_path, entry)
            dst_full_path = os.path.join(dst_path, entry)
            
            if self.is_directory(src_full_path):
                self._copy_directory_recursive(src_full_path, dst_full_path)
            else:
                with self.cephfs_mount.open(src_full_path, 'r') as src_file:
                    with self.cephfs_mount.open(dst_full_path, 'w', mode=0o644) as dst_file:
                        shutil.copyfileobj(src_file, dst_file)
    
    def list_directory(self, path: str = "/", recursive: bool = False) -> List[str]:
        """
        列出目录内容
        
        :param path: 目录路径，默认为根目录
        :param recursive: 是否递归列出子目录
        :return: 文件和目录列表
        """
        try:
            if not self.file_exists(path):
                raise FileNotFoundError(f"目录 {path} 不存在")
            
            if not self.is_directory(path):
                raise NotADirectoryError(f"{path} 不是目录")
            
            if recursive:
                result = []
                self._list_directory_recursive(path, path, result)
                return result
            else:
                return self.cephfs_mount.listdir(path)
        except Exception as e:
            print(f"列出目录失败: {str(e)}")
            return []
    
    def _list_directory_recursive(self, root_path: str, current_path: str, 
                                 result: List[str]) -> None:
        """递归列出目录内容"""
        for entry in self.cephfs_mount.listdir(current_path):
            full_path = os.path.join(current_path, entry)
            rel_path = os.path.relpath(full_path, root_path)
            result.append(rel_path)
            
            if self.is_directory(full_path):
                self._list_directory_recursive(root_path, full_path, result)
    
    def file_exists(self, path: str) -> bool:
        """
        检查文件或目录是否存在
        
        :param path: 文件或目录路径
        :return: 是否存在
        """
        try:
            stat = self.cephfs_mount.stat(path)
            return True
        except cephfs.Error:
            return False
    
    def is_directory(self, path: str) -> bool:
        """
        检查路径是否为目录
        
        :param path: 路径
        :return: 是否为目录
        """
        try:
            stat = self.cephfs_mount.stat(path)
            return stat.st_mode & 0o40000 != 0  # S_IFDIR
        except cephfs.Error:
            return False
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件或目录信息
        
        :param path: 文件或目录路径
        :return: 包含文件信息的字典，如果文件不存在则返回 None
        """
        try:
            stat = self.cephfs_mount.stat(path)
            return {
                'path': path,
                'size': stat.st_size,
                'is_dir': self.is_directory(path),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'accessed_time': stat.st_atime,
                'mode': stat.st_mode,
                'uid': stat.st_uid,
                'gid': stat.st_gid
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
            self.cephfs_mount.makedirs(path, mode=mode)
            return True
        except Exception as e:
            print(f"创建目录失败: {str(e)}")
            return False
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """
        获取 Ceph 集群状态信息
        
        :return: 包含集群状态信息的字典
        """
        try:
            stats = self.rados_cluster.get_cluster_stats()
            return {
                'kb': stats['kb'],
                'kb_used': stats['kb_used'],
                'kb_avail': stats['kb_avail'],
                'num_objects': stats['num_objects']
            }
        except Exception as e:
            print(f"获取集群状态失败: {str(e)}")
            return {}
