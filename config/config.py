
from .yaml_config import load_yaml_config, YamlConfig
import os
import etcd3
import requests
import logging
import json
from urllib.parse import urlparse


def get_plugin_config(config_type: str, config_server: str, plugin_name: str, env: str = "test", file_ext: str = ".yml", app_project: str = "default",local_path: str = None) -> YamlConfig:
    """
    Get plugin configuration from different configuration centers
    
    Args:
        config_type: file/consul/nacos/polaris
        config_server: configuration server address
        plugin_name: name of the plugin
        env: environment (test/prod/dev)
        file_ext: file extension (yml/yaml/json)
    """
    config_filename = f"{plugin_name}-{env}{file_ext}"
    config_file_path = ""
    if config_type == "file":
        config_file_path = os.path.join(local_path, config_filename)
    elif config_type == "consul":
        config_file_path = f"{config_server}/v1/kv/{app_project}/{config_filename}?dc=dc1&raw=true"
    elif config_type == "nacos":
        config_file_path = f"{config_server}/nacos/v1/cs/configs?group={app_project}&dataId={config_filename}"
    elif config_type == "polaris":
        config_file_path = f"{config_server}/config/v1/GetConfigFile?namespace=default&group={app_project}&fileName={config_filename}"
        response = requests.get(config_file_path, timeout=5)
        if response.status_code != 200:
            logging.error(f"Failed to get config from Polaris: {response.status_code}")
            return None
        resp = json.loads(response.text)
        if resp.get("code") != 200000:
            logging.error(f"Polaris config fetch error: {resp.get('message')}")
            return None
        return load_yaml_config(config_data=resp.get("configFile").get("content"))
    elif config_type == "etcd":
        purl = urlparse(config_server)
        host = purl.hostname or "localhost"
        port = purl.port or 2379
        client = etcd3.client(host=host, port=port)
        logging.debug(f"host={host}, etcd={client}")
        key = f"/configs/{app_project}/{config_filename}"
        etcd_value, _ = client.get(key)
        if etcd_value is None:
            logging.error(f"Config not found in etcd for key: {key}")
            return None
        return load_yaml_config(config_data=etcd_value.decode('utf-8'))
    else:
        logging.error(f"Unsupported config type: {config_type}")
        return None
    logging.debug(f"Loading config from: {config_file_path}")
    return load_yaml_config(config_file_path)

