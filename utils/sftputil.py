import paramiko
from paramiko.sftp_client import SFTPClient
from typing import Tuple, Optional

def sftp_connect(
    user: str, 
    password: str, 
    host: str, 
    port: int = 22
) -> Tuple[Optional[SFTPClient], Optional[paramiko.SSHClient], Optional[Exception]]:
    """
    建立SFTP连接
    :return: (sftp客户端, ssh客户端, 错误信息)
    """
    try:
        ssh = paramiko.SSHClient()
        # 自动接受未知主机密钥
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, user, password, timeout=30)
        sftp = ssh.open_sftp()
        return sftp, ssh, None
    except Exception as e:
        return None, None, e

def sftp_close(sftp: SFTPClient, ssh: paramiko.SSHClient) -> None:
    """关闭SFTP和SSH连接"""
    if sftp:
        sftp.close()
    if ssh:
        ssh.close()

def sftp_upload_file(sftp: SFTPClient, local_file_path: str, remote_path: str) -> Optional[Exception]:
    """
    上传文件到SFTP服务器
    :param sftp: SFTP客户端对象
    :param local_file_path: 本地文件路径
    :param remote_path: 远程目录
    """
    try:
        # 获取本地文件名
        file_name = local_file_path.split('/')[-1]
        remote_file_path = f"{remote_path}/{file_name}" if remote_path.endswith('/') else f"{remote_path}/{file_name}"
        # 上传文件
        sftp.put(local_file_path, remote_file_path)
        return None
    except Exception as e:
        return e