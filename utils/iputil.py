import socket
import platform
import subprocess

def get_local_ip_address() -> str:
    """获取本地IP地址"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

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