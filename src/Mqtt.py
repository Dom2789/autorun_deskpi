import threading
from .DataExchange import Data
import paho.mqtt.publish as publish
from time import sleep, strftime

class Mqtt_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topic:str):
        super(Mqtt_Routine, self).__init__()
        self.data = Data()
        self.MQTT_SERVER = broker_IP 
        self.MQTT_PATH = topic

    
    
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

            publish.single(self.MQTT_PATH, string, hostname=self.MQTT_SERVER)
            sleep(10)
