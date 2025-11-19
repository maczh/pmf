import os
import logging
from config import load_yaml_config,get_plugin_config
from db import RedisClient,mongo,mysql
from registry import EtcdRegistry,ConsulRegistry,PolarisClient,NacosRegistry
from fastapi import FastAPI
from utils import iputil
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class App:
    config_file = ""
    app = None
    config = None
    class client:
        mysql = None
        redis = None
        mgo = None
        mqtt = None
        rabbitmq = None
        kafka = None
        etcd = None
        consul = None
        polaris = None
        nacos = None
        s3 = None
        alioss = None

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = load_yaml_config(config_file)
        self.app = FastAPI()
        self.init_clients()

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.config.pmf.application.port.to_primitive())
        
    
    def init_clients(self):
        cfg_server = self.config.pmf.config.server_type.to_primitive()
        cfg_server_addr = self.config.pmf.config.server.to_primitive()
        cfg_env = self.config.pmf.config.env.to_primitive()
        cfg_ext = self.config.pmf.config.type.to_primitive()
        app_project = self.config.pmf.application.project.to_primitive()
        local_path = os.path.dirname(os.path.abspath(__file__))
        used_clients = self.config.pmf.config.used.to_primitive().split(",")
        if "redis" in used_clients:
            redis_config = get_plugin_config(cfg_server, cfg_server_addr, self.config.pmf.config.prefix.redis.to_primitive(), cfg_env, cfg_ext, app_project,local_path)
            logger.debug(f"正在初始化Redis客户端,配置信息为：{redis_config}")
            self.client.redis = RedisClient(host=redis_config.pmf.data.redis.host.to_primitive(), 
                                            port=redis_config.pmf.data.redis.port.to_primitive(),
                                            db=redis_config.pmf.data.redis.database.to_primitive(), 
                                            password=redis_config.pmf.data.redis.password.to_primitive(),
                                            socket_timeout=redis_config.pmf.data.redis.timeout.to_primitive(),
                                            max_connections=redis_config.pmf.data.redis_pool.max.to_primitive()).connect()
            logger.debug(f"Redis客户端初始化完成")
            
        if "mysql" in used_clients:
            mysql_config = get_plugin_config(cfg_server, cfg_server_addr, self.config.pmf.config.prefix.mysql.to_primitive(), cfg_env, cfg_ext, app_project,local_path)
            logger.debug(f"正在初始化MySQL客户端,配置信息为：{mysql_config}")
            self.client.mysql = mysql(uri=mysql_config.pmf.data.mysql.to_primitive(), 
                                      pool_size=mysql_config.pmf.data.mysql_pool.max.to_primitive(),
                                      max_overflow=mysql_config.pmf.data.mysql_pool.total.to_primitive(),
                                      debug=mysql_config.pmf.data.mysql_debug.to_primitive())
            logger.debug(f"MySQL客户端初始化完成")
            
        if "mongo" in used_clients:
            mgo_config = get_plugin_config(cfg_server, cfg_server_addr, self.config.pmf.config.prefix.mongo.to_primitive(), cfg_env, cfg_ext, app_project,local_path)
            logger.debug(f"正在初始化Mongo客户端,配置信息为：{mgo_config}")
            self.client.mgo = mongo(uri=mgo_config.pmf.data.mongodb.uri.to_primitive(), 
                                    db_name=mgo_config.pmf.data.mongodb.db.to_primitive(),
                                    pool_size=mgo_config.pmf.data.mongo_pool.max.to_primitive())
            logger.debug(f"Mongo客户端初始化完成")
            
        if "etcd" in used_clients:
            etcd_config = get_plugin_config(cfg_server, cfg_server_addr, self.config.pmf.config.prefix.etcd.to_primitive(), cfg_env, cfg_ext, app_project,local_path)
            logger.debug(f"正在初始化Etcd客户端,配置信息为：{etcd_config}")
            self.client.etcd = EtcdRegistry(host=etcd_config.pmf.etcd.server.to_primitive(),
                                            port=etcd_config.pmf.etcd.port.to_primitive())
            ips = iputil.local_ipv4s()
            # if etcd_config.pmf.etcd.lan.to_primitive():
                
            
