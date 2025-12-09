import threading
from .DataExchange import Data
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from time import sleep, strftime
import logging

class Mqtt_Subscribe_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topic:str):
        super(Mqtt_Subscribe_Routine, self).__init__()
        self.data = Data()
        self.MQTT_SERVER = broker_IP 
        self.MQTT_PATH = topic
        self._logger = logging.getLogger("Mqtt Sub")
        self._logger.info(f"Broker: {self.MQTT_SERVER}, Topic: {self.MQTT_PATH}")

    
    @staticmethod
    def on_message_print(client, userdata, message):
        print("%s %s" % (message.topic, message.payload))
        userdata["message_count"] += 1
        if userdata["message_count"] >= 5:
            # it's possible to stop the program by disconnecting
            client.disconnect()


    def run(self):
        subscribe.callback(self.on_message_print, self.MQTT_PATH, hostname=self.MQTT_SERVER, userdata={"message_count": 0})