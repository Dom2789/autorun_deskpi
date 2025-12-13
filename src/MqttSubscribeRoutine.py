import threading
from .DataExchange import Data
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from time import sleep, strftime
import logging
import json
from typing import Callable

class Mqtt_Subscribe_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topic:str, parse_func:Callable):
        super(Mqtt_Subscribe_Routine, self).__init__()
        self.data = Data()
        self.MQTT_SERVER = broker_IP 
        self.MQTT_PATH = topic
        self.parse_function = parse_func
        self._logger = logging.getLogger("MQTT_Sub")
        self._logger.info(f" Subscribed to Broker '{self.MQTT_SERVER}' with Topic '{self.MQTT_PATH}'")



    def on_message_print(self, client, userdata, message):
        try:
            userdata["message_count"] += 1
            message_decode = message.payload.decode()  
            logging_string = f"[message count: {userdata["message_count"]}][topic: {message.topic}] [{message_decode}]"          
            json_dict = json.loads(message_decode)
            
            if self.data.led_strip.new_data:
                self._logger.warning(f"Already processing a request! Missed data: {logging_string}")
            else:
                try:
                    self.parse_function(self.data, json_dict)
                    self._logger.info(logging_string)
                except KeyError as e:
                    self._logger.error(f"[Keyerror {e} in parse_function]{logging_string}")

        except Exception as e:
            self._logger.error(f"[{e}]{logging_string}")


    def run(self):
        subscribe.callback(self.on_message_print, self.MQTT_PATH, hostname=self.MQTT_SERVER, userdata= {"message_count":0})
        