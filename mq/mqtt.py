import paho.mqtt.client as mqtt
import logging
import time

class MQTTClient:
    def __init__(self, broker:str, port: int=1883, client_id: str=None, username: str=None, password: str=None, first_reconnect_delay: int=1, reconnect_rate: int=2, max_reconnect_count: int=12, max_reconnect_delay: int=60):
        self.client = mqtt.Client(
            client_id=client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        if username and password:
            self.client.username_pw_set(username, password)
        self.broker = broker
        self.port = port
        # self.client.on_connect = self.on_connect
        self.connect()

    def connect(self):
        self.client.connect(host=self.broker, port=self.port)
        self.client.loop_start()

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topic, qos=0, on_message=None):
        if on_message:
            self.client.on_message = on_message
        self.client.subscribe(topic, qos)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def on_disconnect(self):
        reconnect_count, reconnect_delay = 0, self.first_reconnect_delay
        while reconnect_count < self.max_reconnect_count:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                self.client.connect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= self.reconnect_rate
            reconnect_delay = min(reconnect_delay, self.max_reconnect_delay)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)