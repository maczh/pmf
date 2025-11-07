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
        self.prefix = "services"

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
            key = f"{self.prefix}/{cluster}/{group}/{project}/{service_name}"

            # Register new service instance. python-consul's register() does not
            # return a boolean on success, it raises on failure. Return True when
            # no exception is raised.
            self.consul_client.agent.service.register(
                name=key,
                service_id=instanceId,
                address=service_ip,
                port=service_port,
                tags=[val],
                check=None  # Disable health check for simplicity
            )
            return True

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
            # Get all registered services from the local agent and filter by
            # the full service name we used when registering (key).
            key = f"{self.prefix}/{cluster}/{group}/{project}/{service_name}"
            # services = self.consul_client.agent.services()

            _,instances = self.consul_client.health.service(key, passing=True)
            
            # services is a dict keyed by service_id; values are dicts
            # instances = [s for s in services.values() if s.get('Service') == key]
            # Debug print for visibility when running directly
            # print(f"Discovered instances for {key}: {instances}")

            if not instances:
                return None

            # Randomly select one instance. Prefer the tag value (we stored the
            # URL there). If tags are missing, fall back to address:port.
            instance = random.choice(instances)
            service = instance.get('Service') or instance.get('Service', {})
            tags = service.get('Tags') or []
            if tags:
                # Tags from python-consul are regular strings
                return tags[0]

            address = service.get('Address')
            port = service.get('Port')
            if address and port:
                return f"http://{address}:{port}"

            return None

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
           
            # python-consul deregister does not return a boolean; return True on
            # success (no exception) to match other registry implementations.
            self.consul_client.agent.service.deregister(instanceId)
            return True

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
    # registry.deregister_service("test_service","192.168.2.3",8080)
    # registry.deregister_service("test_service","192.168.2.4",8080)
    # registry.deregister_service("test_service","192.168.2.5",8080)
        