from typing import Callable, Optional, Any, Dict
import threading
import time
import json
import logging
import pika

# /d:/Projects/python/pmgin/mq/rabbit.py
"""
轻量级 RabbitMQ (AMQP) 客户端封装（同步，基于 pika）
包含：创建连接、发布消息、订阅消息（后台线程消费）、关闭连接
"""



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RabbitMQClient:
    """
    RabbitMQ 客户端类（BlockingConnection）
    使用示例：
        client = RabbitMQClient(host='localhost', username='guest', password='guest')
        client.connect()
        client.publish(exchange='ex', routing_key='rk', body={'hello': 'world'})
        def cb(body, properties, header):
            print('got', body)
        client.subscribe(queue='q1', callback=cb, exchange='ex', routing_key='rk')
        ...
        client.close()
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        virtual_host: str = "/",
        username: str = "guest",
        password: str = "guest",
        heartbeat: int = 60,
        blocked_connection_timeout: int = 30,
        reconnect_interval: int = 5,
        exchange: str = "",
        routing_key: str = "",
    ):
        self._params = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username, password),
            heartbeat=heartbeat,
            blocked_connection_timeout=blocked_connection_timeout,
        )
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self._lock = threading.RLock()
        self._consumer_thread: Optional[threading.Thread] = None
        self._stop_consuming = threading.Event()
        self._reconnect_interval = reconnect_interval
        self.exchange = exchange
        self.routing_key = routing_key

    def connect(self, max_retries: int = 3) -> None:
        """建立连接（带简单重试）"""
        with self._lock:
            if self._connection and self._connection.is_open:
                return
            last_exc = None
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info("Connecting to RabbitMQ (attempt %d/%d)...", attempt, max_retries)
                    self._connection = pika.BlockingConnection(self._params)
                    self._channel = self._connection.channel()
                    logger.info("Connected to RabbitMQ")
                    return
                except Exception as e:
                    last_exc = e
                    logger.warning("Connect failed (%s). retry in %ds", e, self._reconnect_interval)
                    time.sleep(self._reconnect_interval)
            logger.error("Failed to connect to RabbitMQ after %d attempts", max_retries)
            raise last_exc

    def close(self) -> None:
        """停止消费并关闭通道与连接"""
        with self._lock:
            # stop consumer thread if running
            if self._consumer_thread and self._consumer_thread.is_alive():
                logger.info("Stopping consumer thread...")
                self._stop_consuming.set()
                try:
                    # ask pika thread to stop consuming safely
                    if self._connection and self._connection.is_open:
                        self._connection.add_callback_threadsafe(lambda: self._channel.stop_consuming())
                except Exception:
                    pass
                self._consumer_thread.join(timeout=5)
                self._consumer_thread = None
                self._stop_consuming.clear()
            try:
                if self._channel and self._channel.is_open:
                    self._channel.close()
                if self._connection and self._connection.is_open:
                    self._connection.close()
            except Exception as e:
                logger.debug("Error closing connection/channel: %s", e)
            finally:
                self._channel = None
                self._connection = None
        logger.info("RabbitMQ client closed")

    def _ensure_connected(self):
        """内部保证已连接"""
        if not (self._connection and self._connection.is_open and self._channel and self._channel.is_open):
            self.connect()

    def publish(
        self,
        exchange: str = "",
        routing_key: str = "",
        body: Any = b"",
        properties: Optional[pika.BasicProperties] = None,
        declare_exchange: bool = False,
        exchange_type: str = "direct",
        durable: bool = True,
        retry: int = 2,
    ) -> None:
        """
        发布消息。
        body: bytes/str 或可 JSON 序列化的对象（会自动转换为 JSON 字符串）
        declare_exchange: 如果为 True，先声明交换机
        """
        if isinstance(body, (dict, list)):
            payload = json.dumps(body).encode("utf-8")
            if properties is None:
                properties = pika.BasicProperties(content_type="application/json")
        elif isinstance(body, str):
            payload = body.encode("utf-8")
        elif isinstance(body, bytes):
            payload = body
        else:
            # 尝试转 json
            payload = json.dumps(body).encode("utf-8")
            if properties is None:
                properties = pika.BasicProperties(content_type="application/json")

        attempt = 0
        last_exc = None
        while attempt <= retry:
            try:
                self._ensure_connected()
                if declare_exchange and exchange:
                    self._channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=durable)
                self._channel.basic_publish(exchange=exchange or self.exchange, routing_key=routing_key or self.routing_key, body=payload, properties=properties)
                return
            except Exception as e:
                last_exc = e
                logger.warning("Publish failed (attempt %d): %s", attempt + 1, e)
                # try to reconnect
                try:
                    self.close()
                except Exception:
                    pass
                time.sleep(self._reconnect_interval)
                try:
                    self.connect()
                except Exception:
                    pass
                attempt += 1
        logger.error("Publish failed after %d attempts", retry + 1)
        raise last_exc

    def subscribe(
        self,
        queue: str,
        callback: Callable[[Any, pika.BasicProperties, Dict[str, Any]], None],
        exchange: Optional[str] = None,
        routing_key: Optional[str] = None,
        exchange_type: str = "direct",
        durable: bool = True,
        auto_ack: bool = False,
        prefetch_count: int = 1,
        declare_queue: bool = True,
    ) -> None:
        """
        订阅队列并在后台线程消费
        callback 参数为 (body, properties, headers)
            body: bytes 或 解码后的 JSON/object（若 content_type 为 application/json，会尝试解析）
            properties: pika.BasicProperties
            headers: properties.headers 或 {}
        """
        if self._consumer_thread and self._consumer_thread.is_alive():
            raise RuntimeError("consumer already running")
        self._stop_consuming.clear()

        def _worker():
            while not self._stop_consuming.is_set():
                try:
                    self.connect()
                    ch = self._channel
                    if not ch:
                        raise RuntimeError("channel not available")
                    if prefetch_count:
                        ch.basic_qos(prefetch_count=prefetch_count)
                    e = exchange if exchange is not None else self.exchange
                    rk = routing_key if routing_key is not None else self.routing_key
                    if e:
                        ch.exchange_declare(exchange=e, exchange_type=exchange_type, durable=durable)
                    if declare_queue:
                        ch.queue_declare(queue=queue, durable=durable)
                    if e and rk:
                        ch.queue_bind(queue=queue, exchange=e, routing_key=rk)

                    def _on_message(ch_inner, method, properties, body):
                        try:
                            payload = body
                            # 尝试根据 content_type 解析 JSON
                            if properties and getattr(properties, "content_type", "") == "application/json":
                                try:
                                    payload = json.loads(body.decode("utf-8"))
                                except Exception:
                                    pass
                            callback(payload, properties, getattr(properties, "headers", {}) or {})
                            if not auto_ack:
                                ch_inner.basic_ack(delivery_tag=method.delivery_tag)
                        except Exception as cb_exc:
                            logger.exception("Error in message callback: %s", cb_exc)
                            # 若不自动 ack，则拒绝并可选择 requeue=False
                            try:
                                if not auto_ack:
                                    ch_inner.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                            except Exception:
                                pass

                    consumer_tag = ch.basic_consume(queue=queue, on_message_callback=_on_message, auto_ack=auto_ack)
                    logger.info("Start consuming queue=%s", queue)
                    # start_consuming 会阻塞，直到 stop_consuming 被调用或发生异常
                    ch.start_consuming()
                except Exception as e:
                    if self._stop_consuming.is_set():
                        break
                    logger.warning("Consumer stopped unexpectedly: %s. Reconnecting in %ds...", e, self._reconnect_interval)
                    try:
                        # close and retry
                        self.close()
                    except Exception:
                        pass
                    time.sleep(self._reconnect_interval)
                    continue
                else:
                    break  # 正常退出循环
            logger.info("Consumer thread exiting for queue=%s", queue)

        self._consumer_thread = threading.Thread(target=_worker, daemon=True)
        self._consumer_thread.start()
