import etcd3
import json
import time
import random
from typing import Dict, List, Optional
from hashlib import md5

class EtcdRegistry:
    def __init__(self, host: str = 'localhost', port: int = 2379):
        """Initialize ETCD client connection"""
        self.client = etcd3.client(host=host, port=port)
        self.prefix = "/services"
        self.lease_ttl = 60  # TTL in seconds

    def register_service(self, service_name: str,service_ip:str, service_port:int,protocol = "http",cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> bool:
        """
        Register a service with ETCD
        Args:
            service_name: Name of the service
            service_info: Dictionary containing service details (host, port, etc.)
        """
        try:
            val = f"{protocol}://{service_ip}:{service_port}"
            # hashlib requires bytes; encode the string before hashing.
            # Use md5(bytes).hexdigest() or update() then hexdigest().
            instanceId = md5(val.encode('utf-8')).hexdigest()
            key = f"{self.prefix}/{cluster}/{group}/{project}/{service_name}/{instanceId}"
            print(f"Registering etcd service with key: {key}, value: {val}")
            lease = self.client.lease(self.lease_ttl)
            resp = self.client.put(key, val, lease=lease)
            print(f"etcd注册结果: {resp}")
            return True
        except Exception as e:
            print(f"Failed to register service: {str(e)}")
            return False

    def discover_service(self, service_name: str,cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> Optional[str]:
        """
        Discover a service by name
        Args:
            service_name: Name of the service to discover
        Returns:
            Service information if found, None otherwise
        """
        try:
            key_prefix = f"{self.prefix}/{cluster}/{group}/{project}/{service_name}/"
            urls = [kv[0].decode() for kv in self.client.get_prefix(key_prefix, keys_only=False)]
            if not urls:
                raise Exception(f"No instances found for service: {service_name}")
            return random.choice(urls)
        except Exception as e:
            print(f"Failed to discover service: {str(e)}")
            return None


    def deregister_service(self, service_name: str,service_ip:str, service_port:int,protocol = "http",cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> bool:
        """
        Deregister a service from ETCD
        Args:
            service_name: Name of the service to deregister
        """
        try:
            val = f"{protocol}://{service_ip}:{service_port}"
            # Ensure we encode the string to bytes before hashing
            instanceId = md5(val.encode('utf-8')).hexdigest()
            key = f"{self.prefix}/{cluster}/{group}/{project}/{service_name}/{instanceId}"
            self.client.delete(key)
            print(f"Deregistered service with key: {key}")
            return True
        except Exception as e:
            print(f"Failed to deregister service: {str(e)}")
            return False


if __name__ == "__main__":
    registry = EtcdRegistry(host='127.0.0.1', port=2379)
    registry.register_service("test_service","192.168.2.3",8080,project="jihai-kmp")
    registry.register_service("test_service","192.168.2.4",8080,project="jihai-kmp")
    registry.register_service("test_service","192.168.2.5",8080,project="jihai-kmp")
    service_url = registry.discover_service("test_service",project="jihai-kmp")
    print(f"Discovered service URL: {service_url}")
    service_url = registry.discover_service("test_service",project="jihai-kmp")
    print(f"Discovered service URL: {service_url}")
    service_url = registry.discover_service("test_service",project="jihai-kmp")
    print(f"Discovered service URL: {service_url}")
    registry.deregister_service("test_service","192.168.2.3",8080,project="jihai-kmp")
    registry.deregister_service("test_service","192.168.2.4",8080,project="jihai-kmp")
    registry.deregister_service("test_service","192.168.2.5",8080,project="jihai-kmp")
