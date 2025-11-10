import sys
import os
# import etcd3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from config.yaml_config import load_yaml_config, YamlConfig
from config.config import get_plugin_config
import logging

logger = logging.getLogger("test_config")
logging.basicConfig(level=logging.DEBUG)

# client = etcd3.client(host='localhost', port=2379)
# key = "configs/jhkmp/mysql-test.yml"
# p = Path("test/mysql-test.yml")
# with p.open("r", encoding="utf-8") as f:
#     file_content = f.read()
# client.put(key, file_content)

app_config = load_yaml_config("test/jh-kry-mp-order.yml")

cfg_server = app_config.go.config.server_type.to_primitive()
cfg_server_addr = app_config.go.config.server.to_primitive()
print(f"Config Server: {cfg_server}, Address: {cfg_server_addr}")
cfg_env = app_config.go.config.env.to_primitive()
cfg_ext = app_config.go.config.type.to_primitive()
app_project = app_config.go.application.project.to_primitive()

plug_name_mysql = app_config.go.config.prefix.mysql.to_primitive()
plug_name_redis = app_config.go.config.prefix.redis.to_primitive()
plug_name_etcd = app_config.go.config.prefix.etcd.to_primitive()

local_path = os.path.dirname(os.path.abspath(__file__))

mysql_config = get_plugin_config(cfg_server, cfg_server_addr, plug_name_mysql, cfg_env, cfg_ext, app_project,local_path)
logger.info(f"MySQL Config: {mysql_config}")
# redis_config = get_plugin_config(cfg_server, cfg_server_addr, plug_name_redis, cfg_env, cfg_ext, app_project,local_path)
# logger.info(f"Redis Config: {redis_config}")
# etcd_config = get_plugin_config(cfg_server, cfg_server_addr, plug_name_etcd, cfg_env, cfg_ext, app_project,local_path)
# logger.info(f"Etcd Config: {etcd_config}")