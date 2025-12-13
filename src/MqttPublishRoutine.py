import threading
from .DataExchange import Data
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from time import sleep, strftime
import logging

class Mqtt_Publish_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topic:str, sleep_time:str="10"):
        super(Mqtt_Publish_Routine, self).__init__()
        self.data = Data()
        self.MQTT_SERVER = broker_IP 
        self.MQTT_PATH = topic
        self._logger = logging.getLogger("MQTT Pub")
        self._logger.info(f"Broker: {self.MQTT_SERVER}, Topic: {self.MQTT_PATH}")
        if sleep_time.isnumeric():
            self.sleep_time = int(sleep_time)
        else:
            logging.error(f"Value '{sleep_time}' given for sleep_time is not a number. sleep_time is set to default value (10).") 
            self.sleep_time = 10
            

    def run(self):
        while True:   
            timestamp = strftime("%H:%M:%S")
            data = self.data.get_data()
            if data is None:
                temp = 0.0
                pres = 0.0
                humi = 0.0
            else:
                temp, pres, humi = data

            string = f"[{timestamp}] [{temp:.2f}C] [{pres:.2f}hPa] [{humi:.2f}%]"  

            self._logger.info(string)
            publish.single(self.MQTT_PATH, string, hostname=self.MQTT_SERVER)
            sleep(self.sleep_time)
