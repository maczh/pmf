import socket
import ipaddress
from typing import List


def get_local_ip_address() -> str:
    """获取本地IP地址"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def get_local_ipv4s() -> List[str]:
    """获取本机所有非环回IPv4地址
    
    Returns:
        List[str]: IPv4地址列表，已去重并排除环回地址
    """
    # 获取本机所有的网络接口信息
    try:
        interfaces = socket.getaddrinfo(socket.gethostname(), None)
    except socket.gaierror:
        # 如果主机名解析失败，尝试使用IP地址
        interfaces = socket.getaddrinfo(socket.gethostbyname(socket.gethostname()), None)
    
    # 提取IPv4地址
    ipv4_addresses = []
    for item in interfaces:
        if item[0] == socket.AF_INET:  # AF_INET 表示IPv4
            address = item[4][0]  # 地址部分在第四个元素中，并以元组形式存在，取第一个元素
            ipv4_addresses.append(address)
    
    return ipv4_addresses

def local_ipv4s() -> list[str]:
    """获取所有非环回IPv4地址"""
    ips = []
    for interface in socket.if_nameindex():
        try:
            addrs = socket.getaddrinfo(interface[1], None)
            for addr in addrs:
                ip = addr[4][0]
                if ip.startswith('127.'):
                    continue
                if '.' in ip:  # IPv4
                    ips.append(ip)
        except Exception:
            continue
    return list(set(ips))

def is_intranet_ip(ip: str) -> bool:
    """判断是否为内网IP"""
    if ip.startswith(('10.', '192.168.')):
        return True
    if ip.startswith('172.'):
        parts = ip.split('.')
        if len(parts) >= 2:
            try:
                second = int(parts[1])
                return 16 <= second <= 31
            except ValueError:
                pass
    return False

def is_port_use(port: int) -> bool:
    """判断端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return False
    except OSError:
        return True
    
if __name__ == "__main__":
    print(get_local_ipv4s())