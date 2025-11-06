import consul
import random
import socket
from hashlib import md5
from typing import Optional, List
from urllib.parse import urlparse

class ConsulRegistry:
    def __init__(self, host: str = "localhost", port: int = 8500):
        """Initialize Consul client."""
        self.consul_client = consul.Consul(host=host, port=port)
        self.prefix = "services/"

    def register_service(self, service_name: str, service_ip: str, service_port: int,protocol = "http",cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> bool:
        """
        Register a service instance with its URL.
        
        Args:
            service_name: Name of the service
            service_url: URL of the service instance (http://host:port)
        """
        try:
            # Validate URL
            val = f"{protocol}://{service_ip}:{service_port}"
            # hashlib requires bytes; encode the string before hashing.
            # Use md5(bytes).hexdigest() or update() then hexdigest().
            instanceId = md5(val.encode('utf-8')).hexdigest()
            key = f"{self.prefix}-{cluster}-{group}-{project}-{service_name}"

            # Delete existing registration if any
            # self.consul_client.agent.service.deregister(instanceId)

            # Register new service instance
            success = self.consul_client.agent.service.register(
                name=service_name,
                service_id=instanceId,
                address=service_ip,
                port=service_port,
                tags=[val]
            )
            return success

        except Exception as e:
            print(f"Error registering service: {str(e)}")
            return False

    def discover_service(self, service_name: str,cluster = "DEFAULT_CLUSTER",group = "DEFAULT_GROUP",project = "DEFAULT_PROJECT") -> Optional[str]:
        """
        Discover a random instance of the specified service.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            Random service URL or None if no services found
        """
        try:
            # Get all instances for the service
            key = f"{self.prefix}/{cluster}/{group}/{project}/{service_name}"
            _, instances = self.consul_client.health.service(key)

            if not instances:
                return None

            # Randomly select one instance
            instance = random.choice(instances)
            return instance['Tags'][0].decode('utf-8')

        except Exception as e:
            print(f"Error discovering service: {str(e)}")
            return None


    def deregister_service(self, service_name: str, service_ip: str, service_port: int,protocol = "http") -> bool:
        """
        Deregister a service instance.
        
        Args:
            service_name: Name of the service
            service_url: URL of the service instance
        """
        try:
            val = f"{protocol}://{service_ip}:{service_port}"
            # hashlib requires bytes; encode the string before hashing.
            # Use md5(bytes).hexdigest() or update() then hexdigest().
            instanceId = md5(val.encode('utf-8')).hexdigest()
           
            return self.consul_client.agent.service.deregister(instanceId)

        except Exception as e:
            print(f"Error deregistering service: {str(e)}")
            return False
        
if __name__ == "__main__":
    registry = ConsulRegistry()
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
        