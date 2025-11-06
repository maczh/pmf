from typing import Optional, Dict, Any
import threading
from redis import Redis, ConnectionPool, RedisError

"""
Redis helper for connecting, checking, getting and closing Redis connections.

Usage:
    client = RedisClient(host='localhost', port=6379)
    r = client.get_connection()
    client.check()  # raises if unreachable
    client.close()
"""




class RedisClient:
    """
    Simple Redis connection manager using a ConnectionPool.

    Methods:
    - connect(): establish pool and client
    - get_connection(): return Redis instance (connects lazily)
    - check(): ping Redis to verify connectivity
    - close(): disconnect pool
    - reconnect(): force reconnect
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        socket_timeout: Optional[float] = None,
        max_connections: Optional[int] = 10,
        decode_responses: bool = True,
        client_name: Optional[str] = None,
        **kwargs: Any,
    ):
        self._conf: Dict[str, Any] = dict(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            max_connections=max_connections,
            decode_responses=decode_responses,
            client_name=client_name,
            **kwargs,
        )
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None
        self._lock = threading.RLock()

    def connect(self) -> Redis:
        """Create connection pool and Redis client. Safe to call multiple times."""
        with self._lock:
            if self._client is not None:
                return self._client
            pool_kwargs = {
                "host": self._conf["host"],
                "port": self._conf["port"],
                "db": self._conf["db"],
                "password": self._conf["password"],
                "socket_timeout": self._conf["socket_timeout"],
                "max_connections": self._conf["max_connections"],
                "decode_responses": self._conf["decode_responses"],
            }
            # Remove None entries to avoid passing them to ConnectionPool if not supported
            pool_kwargs = {k: v for k, v in pool_kwargs.items() if v is not None}
            self._pool = ConnectionPool(**pool_kwargs)
            self._client = Redis(connection_pool=self._pool, client_name=self._conf.get("client_name"))
            return self._client

    def get_connection(self) -> Redis:
        """Return an active Redis client; connect lazily if needed."""
        if self._client is None:
            return self.connect()
        return self._client

    def check(self, timeout: Optional[float] = None) -> bool:
        """
        Check connectivity by sending PING.
        Raises RedisError on failure.
        Returns True if PONG received.
        """
        client = self.get_connection()
        try:
            # ping may accept a timeout depending on redis-py; use socket_timeout for overall behavior
            pong = client.ping()
            return bool(pong)
        except RedisError:
            # re-raise to let caller handle retries/logging
            raise

    def close(self) -> None:
        """Close the connection pool and drop client reference."""
        with self._lock:
            if self._pool is not None:
                try:
                    self._pool.disconnect()
                finally:
                    self._pool = None
                    self._client = None

    def reconnect(self) -> Redis:
        """Force close and create a new connection."""
        with self._lock:
            self.close()
            return self.connect()

    # context manager support
    def __enter__(self) -> "RedisClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


# Example minimal usage (remove or adapt in production):
if __name__ == "__main__":
    client = RedisClient()
    r = client.get_connection()
    try:
        ok = client.check()
        print("Redis reachable:", ok)
        r.select(6)
        r.set("test_key", "test_value")
        val = r.get("test_key")
        print("test_key:", val)
    except Exception as e:
        print("Redis check failed:", e)
    finally:
        client.close()