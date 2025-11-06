import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import declarative_base, sessionmaker, Session


from sqlalchemy import (
    create_engine, Column, BigInteger, String, DateTime, text, engine
)

Base = declarative_base()

class mysql:
    """
    mysql 类
    用于封装基于 SQLAlchemy 的 MySQL 连接与会话管理，提供建立连接、获取会话/引擎、连接检查和关闭资源的便捷方法。
    属性:
        uri (str)
            数据库连接 URI（例如 "mysql+pymysql://user:pass@host/db"）。
        pool_size (int)
            连接池的初始连接数，默认为 2。
        max_overflow (int)
            连接池的最大溢出连接数（超过 pool_size 的额外连接），默认为 10。
        debug (bool)
            是否启用 SQLAlchemy 的 echo（调试输出），默认为 False。
        Engine (sqlalchemy.engine.Engine | None)
            SQLAlchemy Engine 实例，表示与数据库的底层连接引擎。未连接时为 None。
        SessionLocal (sqlalchemy.orm.session.sessionmaker | None)
            sessionmaker 工厂，用于创建 Session 实例。未连接时为 None。
    方法:
        __init__(uri: str, pool_size: int = 2, max_overflow: int = 10, debug: bool = False)
            构造函数，保存连接配置并尝试建立连接（调用 connect）。
            参数:
                uri: 数据库连接字符串。
                pool_size: 连接池大小。
                max_overflow: 最大溢出连接数。
                debug: 是否开启调试输出。
            异常:
                若连接过程中发生错误，会将异常向上传递。
        connect()
            使用当前配置创建 SQLAlchemy Engine 和 sessionmaker。
            行为:
                - 调用 create_engine(..., pool_pre_ping=True, echo=debug, pool_size=..., max_overflow=...)
                - 使用 sessionmaker(autocommit=True, autoflush=True, bind=Engine) 创建 SessionLocal
            异常:
                - 创建引擎或会话失败时抛出异常（并可在外部捕获）。
        get_session() -> sqlalchemy.orm.session.Session
            返回一个新的 Session 实例用于数据库操作。
            行为:
                - 若 SessionLocal 为 None，则先尝试 connect() 建立连接。
                - 调用并返回 SessionLocal()。
            返回:
                - 一个 SQLAlchemy Session 对象。
        get_engine() -> sqlalchemy.engine.Engine
            返回当前的 Engine 实例。
            行为:
                - 若 Engine 为 None，则先尝试 connect() 建立连接。
                - 返回 Engine。
            返回:
                - SQLAlchemy Engine 对象。
        check_connection() -> bool
            检查与数据库的连通性。
            行为:
                - 使用 Engine.connect() 执行简短查询（如 "SELECT 1"）。
                - 成功则返回 True。
                - 失败时打印错误信息、尝试重新 connect()，并返回 False。
            返回:
                - True 表示连接正常，False 表示检查失败并已尝试重连。
        close()
            清理并释放资源。
            行为:
                - 若存在 SessionLocal，调用其 close_all()（关闭所有由该 factory 管理的会话）并将其置为 None。
                - 若存在 Engine，调用 Engine.dispose() 释放底层连接并将其置为 None。
            注意:
                - 调用后需要再次通过 connect() 才能恢复数据库访问。
    线程与安全注意事项:
        - 本类封装了 Engine 和 sessionmaker，但具体的 Session 对象应在各自线程/协程中独立使用与关闭。
        - 若在多线程环境中共享此实例，请确保对 connect/close 等操作的同步以避免竞态条件。
    """
    uri = str
    pool_size = int
    max_overflow = int
    debug = bool
    Engine = engine.Engine
    SessionLocal = sessionmaker
    
    def __init__(self, uri: str,pool_size: int = 2, max_overflow: int = 10, debug: bool = False):
        self.uri = uri
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.debug = debug
        self.connect()


    def connect(self):
        try:
            self.Engine = create_engine(self.uri, pool_pre_ping=True,echo=self.debug,
                                        pool_size=self.pool_size,
                                        max_overflow=self.max_overflow)
            self.SessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=self.Engine)
        except Exception as e:
            print(f"MySQL连接失败: {e}")
            raise e
        
    def get_session(self) -> Session:
        if self.SessionLocal is None:
            self.connect()
        return self.SessionLocal()
    
    def get_engine(self) -> engine.Engine:
        if self.Engine is None:
            self.connect()
        return self.Engine        
    
    def check_connection(self) -> bool:
        try:
            with self.Engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"MySQL连接检查失败: {e}")
            self.connect()
            return False
        
    def close(self):
        if self.SessionLocal:
            self.SessionLocal.close_all()
            self.SessionLocal = None
        if self.Engine:
            self.Engine.dispose()
            self.Engine = None