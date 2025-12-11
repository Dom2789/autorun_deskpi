import threading
from .DataExchange import Data
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from time import sleep, strftime
import logging
import json

class Mqtt_Subscribe_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topic:str):
        super(Mqtt_Subscribe_Routine, self).__init__()
        self.data = Data()
        self.MQTT_SERVER = broker_IP 
        self.MQTT_PATH = topic
        self._logger = logging.getLogger("MQTT_Sub")
        self._logger.info(f"Broker: {self.MQTT_SERVER}, Topic: {self.MQTT_PATH}")


    @staticmethod
    def on_message_print(client, userdata, message):
        try:
            message_decode = message.payload.decode()            
            led = json.loads(message_decode)
            logging.info(f"[topic: {message.topic}] [{message_decode}]")

        except Exception as e:
            logging.error(f"[{e}] [topic: {message.topic}] [{message_decode}]")


    def run(self):
        subscribe.callback(self.on_message_print, self.MQTT_PATH, hostname=self.MQTT_SERVER, userdata={"message_count": 0})