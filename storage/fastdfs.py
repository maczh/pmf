from fdfs_client.client import Fdfs_client
from fdfs_client.exceptions import DataError
import os
from typing import List, Optional, Union

class FastDFSManager:
    def __init__(self, config_path: str = None):
        """
        初始化FastDFS客户端
        :param config_path: FastDFS客户端配置文件路径
        """
        self.client = None
        if config_path and os.path.exists(config_path):
            self.connect(config_path)

    def connect(self, config_path: str) -> bool:
        """
        连接到FastDFS服务器
        :param config_path: FastDFS客户端配置文件路径
        :return: 连接是否成功
        """
        try:
            self.client = Fdfs_client(config_path)
            return True
        except Exception as e:
            print(f"连接FastDFS服务器失败: {str(e)}")
            return False

    def create_bucket(self, bucket_name: str) -> bool:
        """
        创建bucket（在FastDFS中对应创建目录）
        :param bucket_name: bucket名称
        :return: 创建是否成功
        """
        try:
            if self.client:
                # FastDFS中通过上传一个空文件来创建目录
                result = self.client.upload_appender_by_buffer(b'', file_ext_name=bucket_name)
                return result['Status'] == 'Upload successed.'
            return False
        except Exception as e:
            print(f"创建bucket失败: {str(e)}")
            return False

    def list_buckets(self) -> List[str]:
        """
        获取所有bucket列表
        :return: bucket列表
        """
        # FastDFS没有直接列出所有目录的方法
        # 这里需要根据实际业务需求实现
        return []

    def delete_bucket(self, bucket_name: str) -> bool:
        """
        删除bucket
        :param bucket_name: bucket名称
        :return: 删除是否成功
        """
        try:
            if self.client:
                # FastDFS中需要通过文件ID来删除
                # 这里需要先获取bucket下的所有文件，然后逐个删除
                return True
            return False
        except Exception as e:
            print(f"删除bucket失败: {str(e)}")
            return False

    def upload_object(self, file_path: str, bucket_name: str = None) -> Optional[str]:
        """
        上传文件
        :param file_path: 本地文件路径
        :param bucket_name: 可选的bucket名称
        :return: 文件ID
        """
        try:
            if self.client and os.path.exists(file_path):
                result = self.client.upload_by_filename(file_path)
                if result['Status'] == 'Upload successed.':
                    return result['Remote file_id']
            return None
        except Exception as e:
            print(f"上传文件失败: {str(e)}")
            return None

    def get_object(self, file_id: str, local_path: str) -> bool:
        """
        下载文件
        :param file_id: FastDFS文件ID
        :param local_path: 本地保存路径
        :return: 下载是否成功
        """
        try:
            if self.client:
                result = self.client.download_to_file(file_id, local_path)
                return result['Status'] == 'Download successed.'
            return False
        except Exception as e:
            print(f"下载文件失败: {str(e)}")
            return False

    def list_objects(self, bucket_name: str = None) -> List[str]:
        """
        列出对象列表
        :param bucket_name: 可选的bucket名称
        :return: 对象列表
        """
        # FastDFS没有直接列出目录下文件的方法
        # 这里需要根据实际业务需求实现
        return []

    def delete_object(self, file_id: str) -> bool:
        """
        删除文件
        :param file_id: FastDFS文件ID
        :return: 删除是否成功
        """
        try:
            if self.client:
                result = self.client.delete_file(file_id)
                return result['Status'] == 'Delete file successed.'
            return False
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False

    def rename_object(self, file_id: str, new_name: str) -> bool:
        """
        重命名文件
        :param file_id: FastDFS文件ID
        :param new_name: 新文件名
        :return: 重命名是否成功
        """
        try:
            if self.client:
                # FastDFS不支持直接重命名
                # 需要先下载文件，然后用新名称重新上传
                temp_path = f"temp_{new_name}"
                if self.get_object(file_id, temp_path):
                    new_file_id = self.upload_object(temp_path)
                    if new_file_id:
                        self.delete_object(file_id)
                        os.remove(temp_path)
                        return True
                return False
        except Exception as e:
            print(f"重命名文件失败: {str(e)}")
            return False

    def get_object_url(self, file_id: str, expires_in: int = 3600) -> Optional[str]:
        """
        获取文件的HTTP URL
        :param file_id: FastDFS文件ID
        :param expires_in: URL过期时间（秒）
        :return: HTTP URL
        """
        try:
            if self.client:
                # FastDFS的URL格式为：http://tracker_server/file_id
                # 这里需要根据实际配置的tracker server地址来构建URL
                tracker_server = "http://tracker_server"  # 需要替换为实际的tracker server地址
                return f"{tracker_server}/{file_id}"
            return None
        except Exception as e:
            print(f"获取文件URL失败: {str(e)}")
            return None
