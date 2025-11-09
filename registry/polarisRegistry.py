# python
import hashlib
import json
import logging
import random
from typing import Optional, Any, Dict

import requests

logger = logging.getLogger("polaris")
logging.basicConfig(level=logging.DEBUG)

def get_instance_id(ip: str, port: int) -> str:
    s = f"http://{ip}:{port}"
    md5v = hashlib.md5(s.encode("utf-8")).hexdigest()
    return md5v[:4]

class PolarisClient:
    def __init__(self, server_addr: str = "http://127.0.0.1:8090",
                 namespace: str = "default",
                 token: str = "",
                 timeout: int = 5,
                 weight: int = 0,
                 ):
        self.api_base_url: str = server_addr
        self.namespace: str = namespace
        self.token: str = token
        self.timeout: int = timeout
        self.weight: int = weight
        self.prefix = "services"

    def register_service(self, service_name: str,service_ip:str, service_port:int,protocol = "http",cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> bool:
        # 创建服务
        service_url = f"{self.api_base_url}/naming/v1/services"
        key = f"{cluster}.{group}.{project}.{service_name}"
        create_service_req = [{"name": key, "namespace": self.namespace}]
        headers = {"X-Polaris-Token": self.token} if self.token else {}
        try:
            resp = requests.post(service_url, headers=headers, json=create_service_req, timeout=5)
            resp_json = resp.json()
            logger.debug("创建服务响应: %s", json.dumps(resp_json))
            code = resp_json.get("code")
            info = resp_json.get("info", "")
            # SUCCESS 或 EXISTS 的常量不确定，保守判断 0 或 200 或自定义
            if code not in (400201, 200000, "SUCCESS", "EXISTS") and code is not None:
                logger.error("Polaris 服务创建失败: %s", info)
                # 继续尝试注册实例也许服务已存在
        except Exception as e:
            logger.error("Polaris 服务创建失败: %s", e)

        # 注册服务实例
        instance_url = f"{self.api_base_url}/naming/v1/instances"
        register_req = [{
            "service": key,
            "namespace": self.namespace,
            "host": service_ip,
            "port": service_port,
            "weight": self.weight,
            "metadata": {"protocol": protocol},
        }]
        logger.debug("注册实例请求参数: %s", json.dumps(register_req))
        try:
            resp = requests.post(instance_url, headers=headers, json=register_req, timeout=5)
            resp_json = resp.json()
            logger.debug("注册实例响应: %s", json.dumps(resp_json))
            code = resp_json.get("code")
            if code not in (400201, 200000, "SUCCESS", "EXISTS") and code is not None:
                logger.error("Polaris 服务实例注册失败: %s", json.dumps(resp_json))
                return False
            self.instanceId = resp_json.get("responses", [{}])[0].get("instance",{}).get("id")
            logger.debug("%s 服务注册成功,实例id为: %s", service_name,self.instanceId)
        except Exception as e:
            logger.error("Polaris 服务实例注册失败: %s", e)
            return False
        return True

    def discover_service(self, service_name: str,cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> Optional[str]:
        serviceName = f"{cluster}.{group}.{project}.{service_name}"
        headers = {"X-Polaris-Token": self.token} if self.token else {}
        params = {"service": serviceName, "namespace": self.namespace}
        try:
            resp = requests.get(f"{self.api_base_url}/naming/v1/instances", headers=headers, params=params, timeout=5)
            res_json = resp.json()
            logger.debug("查询服务实例响应: %s", json.dumps(res_json))
            code = res_json.get("code")
            if code not in (0, 200000, "SUCCESS") and code is not None:
                logger.error("Polaris 查询服务实例失败: %s", res_json.get("Info", ""))
                return None
            instances = res_json.get("instances", [])
            if not instances:
                return None
            ins = random.choice(instances)
            metadata = ins.get("metadata") or {}
            protocol = metadata.get("protocol") or "http"
            host = ins.get("host")
            port = ins.get("port")
            if host and port is not None:
                return f"{protocol}://{host}:{port}"
        except Exception as e:
            logger.error("Polaris 查询服务实例失败: %s", e)
            return None

    def deregister_service(self,service_name: str,service_ip:str, service_port:int,protocol = "http",cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> bool:
        key = f"{cluster}.{group}.{project}.{service_name}"
        query: Dict[str, Any] = {
            # "id": self.instanceId,
            "service": key,
            "namespace": self.namespace,
            "host": service_ip,
            "port": service_port,
        }
        headers = {"X-Polaris-Token": self.token} if self.token else {}
        try:
            resp = requests.post(f"{self.api_base_url}/naming/v1/instances/delete", headers=headers, json=[query], timeout=5)
            res_json = resp.json()
            logger.debug("注销实例响应: %s", json.dumps(res_json))
            code = res_json.get("code")
            if code not in (0, 200000, "SUCCESS") and code is not None:
                logger.error("Polaris 服务实例注销失败: %s", res_json.get("info", ""))
                return False
        except Exception as e:
            logger.error("Polaris 服务实例注销失败: %s", e)
            return False

        # 查询服务是否存在其他实例
        params = {"service": key , "namespace": self.namespace}
        try:
            resp = requests.get(f"{self.api_base_url}/naming/v1/instances", headers=headers, params=params, timeout=5)
            res_json = resp.json()
            logger.debug("查询服务实例响应: %s", json.dumps(res_json))
            code = res_json.get("code")
            if code not in (0, 200000, "SUCCESS") and code is not None:
                logger.error("Polaris 查询服务实例失败: %s", res_json.get("info", ""))
                return True
            instances = res_json.get("instances", [])
            if instances:
                # 仍有其他实例，不注销服务
                return True
        except Exception as e:
            logger.error("Polaris 查询服务实例失败: %s", e)
            return True

        # 注销服务
        try:
            resp = requests.post(f"{self.api_base_url}/naming/v1/services/delete", headers=headers, json=[{"name": key, "namespace": self.namespace}], timeout=5)
            res_json = resp.json()
            logger.debug("注销服务响应: %s", json.dumps(res_json))
            code = res_json.get("code")
            if code not in (0, 200000, "SUCCESS") and code is not None:
                logger.error("Polaris 服务注销失败: %s", res_json.get("Info", ""))
                return True
        except Exception as e:
            logger.error("Polaris 服务注销失败: %s", e)
            return True

if __name__ == "__main__":
    registry = PolarisClient(server_addr="http://192.168.2.3:8090", namespace="default", token="nu/0WRA4EqSR1FagrjRj0fZwPXuGlMpX+zCuWu4uMqy8xr1vRjisSbA25aAC3mtU8MeeRsKhQiDAynUR09I=")
    # registry.register_service("test_service","192.168.2.3",8080,project="jihai-kmp")
    # registry.register_service("test_service","192.168.2.4",8080,project="jihai-kmp")
    # registry.register_service("test_service","192.168.2.5",8080,project="jihai-kmp")
    service_url = registry.discover_service("test_service",project="jihai-kmp")
    print(f"Discovered service URL: {service_url}")
    # service_url = registry.discover_service("test_service",project="jihai-kmp")
    # print(f"Discovered service URL: {service_url}")
    # service_url = registry.discover_service("test_service",project="jihai-kmp")
    # print(f"Discovered service URL: {service_url}")
    registry.deregister_service("test_service","192.168.2.3",8080)
    registry.deregister_service("test_service","192.168.2.4",8080)
    registry.deregister_service("test_service","192.168.2.5",8080)
    