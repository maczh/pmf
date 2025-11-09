import os
import re
import requests
from typing import Tuple, Optional

def download_file(file_url: str, local_path: str) -> Tuple[str, Optional[Exception]]:
    """
    下载文件并保存到本地
    :param file_url: 文件URL
    :param local_path: 本地保存目录
    :return: (本地文件路径, 错误信息)
    """
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # 抛出HTTP错误
        
        # 处理Content-Disposition获取文件名
        disposition = response.headers.get('content-disposition') or response.headers.get('Content-Disposition', '')
        file_name = os.path.basename(file_url)
        
        if disposition:
            # 提取filename中的扩展名
            match = re.search(r'filename=.*?(\.\w+)', disposition)
            if match:
                ext = match.group(1)
                # 替换原文件名的扩展名
                name_without_ext = os.path.splitext(file_name)[0]
                file_name = f"{name_without_ext}{ext}"
        
        # 确保本地目录存在
        os.makedirs(local_path, exist_ok=True)
        local_file_path = os.path.join(local_path, file_name)
        
        # 保存文件
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return local_file_path, None
    except Exception as e:
        return "", e