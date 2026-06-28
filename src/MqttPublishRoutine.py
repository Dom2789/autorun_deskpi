import threading, psutil
from .DataExchange import Data
import paho.mqtt.publish as publish
from time import sleep, strftime
import logging
from vcgencmd import Vcgencmd

class Mqtt_Publish_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topics:dict[str,str], sleep_time:str="10"):
        super(Mqtt_Publish_Routine, self).__init__()
        self.data = Data()
        self.vcgm = Vcgencmd()
        self.MQTT_SERVER = broker_IP 
        self.topics = topics
        self._logger = logging.getLogger("MQTT Pub")
        self._logger.info(f"Broker: {self.MQTT_SERVER}, Topics: {topics}")
        self.timestamp = ""
        if sleep_time.isnumeric():
            self.sleep_time = int(sleep_time)
        else:
            self._logger.error(f"Value '{sleep_time}' given for sleep_time is not a number. sleep_time is set to default value (10).") 
            self.sleep_time = 10

    def run(self):
        while True:
            self.timestamp = strftime("%H:%M:%S")

            payload = self.payload_climate()
            self.publish_payload(self.topics["climate"],payload)

            payload = self.payload_climate_homeassistant()
            if payload != "":
                self.publish_payload(self.topics["climateHA"],payload)

            payload = self.payload_cpu_temp()
            self.publish_payload(self.topics["cpu"], payload)

            sleep(self.sleep_time)

    def payload_climate(self):

        data = self.data.climate_tupel
        if data is None:
            temp = 0.0
            pres = 0.0
            humi = 0.0
        else:
            temp, pres, humi = data

        string = f"[{self.timestamp}] [{temp:.2f}C] [{pres:.2f}hPa] [{humi:.2f}%]"

        return string

    def payload_climate_homeassistant(self):
        data = self.data.climate_tupel
        if data is None:
            return ""
        else:
            temp, pres, humi = data

        string = f'{{"temp":{temp:.2f},"pressure":{pres:.2f},"humidity":{humi:.2f}}}'
        return string

    def payload_cpu_temp(self):
        cpu = psutil.cpu_percent(interval=1)
        string = f"[{self.timestamp}] [temp: {self.vcgm.measure_temp()}°C] [load: {cpu}%]"

        return string

    def publish_payload(self, topic:str, payload:str):
        try:
            publish.single(topic, payload, hostname=self.MQTT_SERVER)
            self._logger.info(payload)
        except TimeoutError as e:
            self._logger.warning(f"[{e}][{payload}")

