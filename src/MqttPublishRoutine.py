import threading, psutil
from .DataExchange import Data
import paho.mqtt.publish as publish
from time import sleep, strftime
import logging
from vcgencmd import Vcgencmd
import glob

class Mqtt_Publish_Routine(threading.Thread):
    def __init__(self, broker_IP:str, topics:dict[str,str], dir_1wire:str ,sleep_time:str="10"):
        super(Mqtt_Publish_Routine, self).__init__()
        self.data = Data()
        self.vcgm = Vcgencmd()
        self.MQTT_SERVER = broker_IP 
        self.topics = topics
        self._logger = logging.getLogger("MQTT Pub")
        self._logger.info(f"Broker: {self.MQTT_SERVER}, Topics: {topics}")
        self.timestamp = ""
        # Finds the first device folder that starts with "28", specific to DS18B20
        device_folder = glob.glob(dir_1wire + "28*")[0]
        # Device file containing the temperature data
        self.onewire_device_file = device_folder + "/w1_slave"
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

            payload = self.payload_outside_temperature()
            if payload != "":
                self.publish_payload(self.topics["outside"], payload)

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

    def payload_outside_temperature(self):
        # Reads raw temperature data from the sensor
        f = open(self.onewire_device_file, "r")
        lines = f.readlines()
        # Parses the raw temperature data and converts it to Celsius and Fahrenheit
        if lines[0].strip()[-3:] == "YES":
            equals_pos = lines[1].find("t=")
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0  # Convert to Celsius
                # build JSON-string for home assistant
                string = f'{{"temp":{temp_c:.2f}}}'
                return string
        return ""

    def helper_read_temp_raw(self) -> list[str]:
        # Reads raw temperature data from the sensor
        f = open(self.onewire_device_file, "r")
        lines = f.readlines()
        f.close()
        return lines

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
