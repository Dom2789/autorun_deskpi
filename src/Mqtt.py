import threading
from .DataExchange import Data
import paho.mqtt.publish as publish
from time import sleep

class Mqtt_Routine(threading.Thread):
    def __init__(self):
        super(Mqtt_Routine, self).__init__()
        self.MQTT_SERVER = "192.168.178.100"
        self.MQTT_PATH = "test_channel"

    
    
    def run(self):
        while True:    
            print("send")        
            publish.single(self.MQTT_PATH, "Hello World!", hostname=self.MQTT_SERVER)
            sleep(5)