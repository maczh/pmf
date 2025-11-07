# python
import hashlib
import json
import logging
import random
import socket
import time
import ipaddress
from typing import List, Tuple, Optional, Any, Dict

import requests
import yaml

logger = logging.getLogger("polaris")
logging.basicConfig(level=logging.INFO)

# 简单内存缓存，模拟 Go 代码中的 cache.OnGetCache("polaris")
_cache: Dict[str, Dict[str, Any]] = {}
def cache_set(namespace: str, key: str, value: Any):
    _cache.setdefault(namespace, {})[key] = value

def cache_get(namespace: str, key: str):
    ns = _cache.get(namespace, {})
    if key in ns:
        return ns[key], True
    return None, False

def cache_delete(namespace: str, key: str):
    ns = _cache.get(namespace, {})
    if key in ns:
        del ns[key]

def to_json(o: Any) -> str:
    try:
        return json.dumps(o, ensure_ascii=False)
    except Exception:
        return "{}"

def get_instance_id(ip: str, port: int) -> str:
    s = f"http://{ip}:{port}"
    md5v = hashlib.md5(s.encode("utf-8")).hexdigest()
    return md5v[:4]

def local_ipv4s(lan: bool, lan_network: str) -> Tuple[List[str], Optional[Exception]]:
    """
    返回符合条件的 IPv4 列表（优先根据 lan 和 lan_network 筛选）
    尝试从所有接口解析可能的 IPv4 地址；若失败则使用 hostname 解析作为后备。
    """
    ips: List[str] = []
    ip_lans: List[str] = []
    ip_wans: List[str] = []
    try:
        host_name = socket.gethostname()
        addrs = socket.getaddrinfo(host_name, None, family=socket.AF_INET)
        seen = set()
        for addr in addrs:
            ip = addr[4][0]
            if ip in seen:
                continue
            seen.add(ip)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                ip_lans.append(ip)
                if lan and (lan_network == "" or ip.startswith(lan_network)):
                    ips.append(ip)
            else:
                ip_wans.append(ip)
                if not lan:
                    ips.append(ip)
        # 如果没有找到匹配，根据 lan 取相反集合作为后备
        if not ips:
            if lan:
                ips.extend(ip_wans)
            else:
                ips.extend(ip_lans)
        # 最后仍为空则使用 127.0.0.1
        if not ips:
            ips.append("127.0.0.1")
        return ips, None
    except Exception as e:
        # 后备：尝试直接解析主机名/IP
        try:
            ip = socket.gethostbyname(socket.gethostname())
            return [ip], None
        except Exception:
            return [], e

class PolarisClient:
    def __init__(self, server_addr: str = "http://127.0.0.1:8090", namespace: str = "default", token: str = "", timeout: int = 5):
        self.api_base_url: str = server_addr
        self.namespace: str = namespace
        self.token: str = token
        self.timeout: int = timeout
        self.weight: int = 0
        self.lan: bool = False
        self.lan_network: str = ""
        self.conf: Dict[str, Any] = {}
        self.conf_data: Optional[bytes] = None

    def register(self, registry_config_data: Optional[bytes] = None):
        if registry_config_data is not None:
            self.conf_data = registry_config_data
        if not self.conf and self.conf_data:
            try:
                self.conf = yaml.safe_load(self.conf_data) or {}
            except Exception as e:
                logger.error("Polaris 配置解析错误: %s", e)
                self.conf = {}
                return

            # 读取配置键（与 Go 版本的 koanf 键类似）
            # 优先读取 go.polaris.*，回退到 polarise keys 或空值
            def conf_get(path: str, default=None):
                parts = path.split(".")
                cur = self.conf
                for p in parts:
                    if isinstance(cur, dict) and p in cur:
                        cur = cur[p]
                    else:
                        return default
                return cur

            self.token = conf_get("go.polaris.token", "")
            self.lan = bool(conf_get("go.polaris.lan", False))
            self.lan_network = conf_get("go.polaris.lanNet", "")
            ipstr = conf_get("go.polaris.server", "")
            portstr = str(conf_get("go.polaris.port", ""))
            if ipstr and portstr:
                self.api_base_url = f"http://{ipstr}:{portstr}"
            self.namespace = conf_get("go.polaris.namespace", "") or "default"

        # 从配置中读取应用信息（期望配置中含 app 信息）
        app = self.conf.get("app") or self.conf.get("go", {}).get("app") or {}
        app_name = app.get("name") or "app"
        app_port = int(app.get("port") or 0)
        app_port_ssl = int(app.get("portSSL") or 0)
        app_ip = app.get("ipAddr") or ""

        local_ips, _ = local_ipv4s(self.lan, self.lan_network)
        ip = local_ips[0] if local_ips else "127.0.0.1"
        if app_ip:
            ip = app_ip

        # 创建服务
        service_url = f"{self.api_base_url}/naming/v1/services"
        create_service_req = [{"Name": app_name, "Namespace": self.namespace}]
        headers = {"X-Polaris-Token": self.token} if self.token else {}
        try:
            resp = requests.post(service_url, headers=headers, json=create_service_req, timeout=5)
            resp_json = resp.json()
            code = resp_json.get("Code")
            info = resp_json.get("Info", "")
            # SUCCESS 或 EXISTS 的常量不确定，保守判断 0 或 200 或自定义
            if code not in (0, 200, "SUCCESS", "EXISTS") and code is not None:
                logger.error("Polaris 服务创建失败: %s", info)
                # 继续尝试注册实例也许服务已存在
        except Exception as e:
            logger.error("Polaris 服务创建失败: %s", e)

        # 注册服务实例
        instance_url = f"{self.api_base_url}/naming/v1/instances"
        register_req = [{
            "Service": app_name,
            "Namespace": self.namespace,
            "Host": ip,
            "Port": app_port if app_port != 0 else app_port_ssl,
            "Weight": self.weight,
            "Metadata": {"ssl": "false"},
        }]
        if app_port_ssl and app_port_ssl != 0:
            register_req[0]["Port"] = app_port_ssl
            register_req[0]["Metadata"]["ssl"] = "true"

        # 补充健康和协议字段（Polaris API 可能在请求体期望）
        register_req[0]["Healthy"] = True
        register_req[0]["Protocol"] = "http" if register_req[0]["Metadata"]["ssl"] == "false" else "https"

        logger.debug("注册实例请求参数: %s", to_json(register_req))
        try:
            resp = requests.post(instance_url, headers=headers, json=register_req, timeout=5)
            resp_json = resp.json()
            code = resp_json.get("Code")
            if code not in (0, 200, "SUCCESS", "EXISTS") and code is not None:
                logger.error("Polaris 服务实例注册失败: %s", to_json(resp_json))
                return
            # 尝试读取 instance id
            responses = resp_json.get("Responses") or []
            service_id = None
            if responses and isinstance(responses, list):
                first = responses[0]
                instance = first.get("Instance") if isinstance(first, dict) else None
                if instance:
                    service_id = instance.get("Id")
            if service_id:
                cache_set("polaris", "serviceId", service_id)
            logger.info("%s 服务注册成功", app_name)
        except Exception as e:
            logger.error("Polaris 服务实例注册失败: %s", e)
            return

    def get_service_url(self, servicename: str, *namespaces: str) -> Tuple[str, str]:
        current_namespace = self.namespace
        namespace_list = list(namespaces) if namespaces else [self.namespace]
        if namespace_list[0] == "":
            namespace_list[0] = self.namespace

        headers = {"X-Polaris-Token": self.token} if self.token else {}
        for ns in namespace_list:
            params = {"service": servicename, "namespace": ns}
            try:
                resp = requests.get(f"{self.api_base_url}/naming/v1/instances", headers=headers, params=params, timeout=5)
                res_json = resp.json()
                code = res_json.get("Code")
                if code not in (0, 200, "SUCCESS") and code is not None:
                    logger.error("Polaris 查询服务实例失败: %s", res_json.get("Info", ""))
                    continue
                instances = res_json.get("Instances", [])
                if not instances:
                    continue
                current_namespace = ns
                ins = random.choice(instances)
                protocol = "http"
                metadata = ins.get("Metadata") or {}
                if metadata.get("ssl") == "true":
                    protocol = "https"
                host = ins.get("Host")
                port = ins.get("Port")
                if host and port is not None:
                    return f"{protocol}://{host}:{port}", current_namespace
            except Exception as e:
                logger.error("Polaris 查询服务实例失败: %s", e)
                continue
        return "", current_namespace

    def deregister(self):
        query: Dict[str, Any] = {}
        service_id, exists = cache_get("polaris", "serviceId")
        if exists and service_id:
            query["ID"] = service_id
        else:
            local_ips, _ = local_ipv4s(self.lan, self.lan_network)
            ip = local_ips[0] if local_ips else "127.0.0.1"
            app = self.conf.get("app") or {}
            if app.get("ipAddr"):
                ip = app.get("ipAddr")
            query["Service"] = app.get("name") or "app"
            query["Namespace"] = self.namespace
            query["Host"] = ip
            port = int(app.get("port") or 0)
            if port == 0 or int(app.get("portSSL") or 0) != 0:
                port = int(app.get("portSSL") or port)
            query["Port"] = port

        headers = {"X-Polaris-Token": self.token} if self.token else {}
        try:
            requests.post(f"{self.api_base_url}/naming/v1/instances/delete", headers=headers, json=[query], timeout=5)
        except Exception as e:
            logger.error("Polaris 服务实例注销失败: %s", e)
            return
        cache_delete("polaris", "serviceId")

        # 查询服务是否存在其他实例
        app = self.conf.get("app") or {}
        params = {"service": app.get("name") or "app", "namespace": self.namespace}
        try:
            resp = requests.get(f"{self.api_base_url}/naming/v1/instances", headers=headers, params=params, timeout=5)
            res_json = resp.json()
            code = res_json.get("Code")
            if code not in (0, 200, "SUCCESS") and code is not None:
                logger.error("Polaris 查询服务实例失败: %s", res_json.get("Info", ""))
                return
            instances = res_json.get("Instances", [])
            if instances:
                # 仍有其他实例，不注销服务
                return
        except Exception as e:
            logger.error("Polaris 查询服务实例失败: %s", e)
            return

        # 注销服务
        try:
            resp = requests.post(f"{self.api_base_url}/naming/v1/services/delete", headers=headers, json=[{"name": app.get("name") or "app", "namespace": self.namespace}], timeout=5)
            res_json = resp.json()
            code = res_json.get("Code")
            if code not in (0, 200, "SUCCESS") and code is not None:
                logger.error("Polaris 服务注销失败: %s", res_json.get("Info", ""))
                return
        except Exception as e:
            logger.error("Polaris 服务注销失败: %s", e)
            return
