from typing import List, Dict, Optional
import json
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin, urlencode

# /d:/Work/python/pmf/registry/nacosRegistry.py
"""
NacosRegistry - 使用 Nacos 作为服务注册中心的简单 Python 客户端

提供：
- register_service(service_name, ip, port, metadata=None, cluster=None, ephemeral=True, weight=1)
- discover_service(service_name, healthy_only=True)
- deregister_service(service_name, ip, port, cluster=None, ephemeral=True)

依赖：requests
"""



class NacosRegistry:
    def __init__(
        self,
        server_addr: str = "http://127.0.0.1:8848",
        namespace: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 5.0,
    ):
        """
        server_addr: nacos server 地址，带协议，例如 http://127.0.0.1:8848
        namespace: 可选的 namespaceId
        username/password: 如果提供，会尝试登录获取 accessToken（适用于开启鉴权的 nacos）
        """
        if not server_addr.startswith("http"):
            server_addr = "http://" + server_addr
        if not server_addr.endswith("/"):
            server_addr += "/"
        self.base = server_addr  # 确保以 / 结尾
        self.namespace = namespace
        self.timeout = timeout
        self.session = requests.Session()
        self.access_token = None
        if username is not None and password is not None:
            # Nacos 登录接口：/nacos/v1/auth/login?username=xxx&password=yyy
            try:
                resp = self.session.get(
                    urljoin(self.base, "nacos/v1/auth/login"),
                    params={"username": username, "password": password},
                    timeout=self.timeout,
                )
                if resp.ok:
                    # 返回的是 token 的纯文本
                    token = resp.text.strip().strip('"')
                    if token:
                        self.access_token = token
                else:
                    # fallback to basic auth header if login fails
                    self.session.auth = HTTPBasicAuth(username, password)
            except Exception:
                self.session.auth = HTTPBasicAuth(username, password)

    def _build_params(self, params: Optional[Dict] = None) -> Dict:
        p = {} if params is None else dict(params)
        if self.namespace:
            p["namespaceId"] = self.namespace
        if self.access_token:
            p["accessToken"] = self.access_token
        return p

    def register_service(
        self,
        service_name: str,
        ip: str,
        port: int,
        metadata: Optional[Dict] = None,
        cluster: Optional[str] = None,
        ephemeral: bool = True,
        weight: float = 1.0,
        enabled: bool = True,
        healthy: bool = True,
    ) -> bool:
        """
        注册实例到 Nacos
        返回 True 表示请求已成功（HTTP 200），不代表后端持久化状态（Nacos 返回 ok 或空响应则视为成功）
        """
        url = urljoin(self.base, "nacos/v1/ns/instance")
        params = {
            "serviceName": service_name,
            "ip": ip,
            "port": port,
            "ephemeral": "true" if ephemeral else "false",
            "weight": str(weight),
            "enabled": "true" if enabled else "false",
            "healthy": "true" if healthy else "false",
        }
        if cluster:
            params["clusterName"] = cluster
        if metadata:
            # 将 metadata 作为 JSON 字符串传递
            params["metadata"] = json.dumps(metadata, separators=(",", ":"))
        try:
            resp = self.session.post(url, params=self._build_params(params), timeout=self.timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def deregister_service(
        self,
        service_name: str,
        ip: str,
        port: int,
        cluster: Optional[str] = None,
        ephemeral: bool = True,
    ) -> bool:
        """
        注销实例
        """
        url = urljoin(self.base, "nacos/v1/ns/instance")
        params = {
            "serviceName": service_name,
            "ip": ip,
            "port": port,
            "ephemeral": "true" if ephemeral else "false",
        }
        if cluster:
            params["clusterName"] = cluster
        try:
            resp = self.session.delete(url, params=self._build_params(params), timeout=self.timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def discover_service(self, service_name: str, healthy_only: bool = True) -> List[Dict]:
        """
        服务发现：返回实例列表（每个实例为 dict，包含 ip, port, metadata, weight, enabled, healthy, clusterName）
        若请求失败返回空列表
        """
        # 尝试使用 instances 接口
        url = urljoin(self.base, "nacos/v1/ns/instances")
        params = {"serviceName": service_name, "healthyOnly": "true" if healthy_only else "false"}
        try:
            resp = self.session.get(url, params=self._build_params(params), timeout=self.timeout)
            if not resp.ok:
                return []
            data = None
            try:
                data = resp.json()
            except ValueError:
                # 非 JSON，返回空
                return []
            # 可能的返回格式:
            # 1) { "hosts": [ {...}, ... ] }
            # 2) { "instances": [ {...}, ... ] }
            hosts = None
            if isinstance(data, dict):
                if "hosts" in data:
                    hosts = data["hosts"]
                elif "instances" in data:
                    hosts = data["instances"]
                elif "hosts" not in data and "instances" not in data and "dom" in data and "hosts" in data:
                    hosts = data.get("hosts", [])
            if hosts is None:
                # 有些 Nacos 版本直接返回 list
                if isinstance(data, list):
                    hosts = data
                else:
                    return []
            result = []
            for h in hosts:
                # h 可能是 dict，也可能是其他格式，尽量提取常用字段
                if not isinstance(h, dict):
                    continue
                item = {
                    "ip": h.get("ip") or h.get("host") or h.get("hostIp"),
                    "port": int(h.get("port")) if h.get("port") is not None else None,
                    "metadata": h.get("metadata") or {},
                    "weight": float(h.get("weight")) if h.get("weight") is not None else None,
                    "enabled": h.get("enabled"),
                    "healthy": h.get("healthy"),
                    "clusterName": h.get("clusterName") or h.get("cluster"),
                }
                result.append(item)
            return result
        except requests.RequestException:
            return []