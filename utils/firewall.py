import subprocess
import sys
from typing import List

def add_ports_to_firewall(ports: List[int]) -> None:
    """
    添加端口到防火墙（仅支持Linux firewalld）
    :param ports: 端口列表
    """
    if sys.platform != 'linux':
        print("仅支持Linux系统")
        return
        
    for port in ports:
        try:
            # 添加TCP端口并永久生效
            subprocess.run(
                ['firewall-cmd', f'--add-port={port}/tcp', '--permanent'],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"端口 {port} 添加成功")
        except subprocess.CalledProcessError as e:
            print(f"添加端口 {port} 失败: {e.stderr}")