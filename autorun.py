#!/usr/bin/python3
from src.DisplayRoutine import Display_Routine
from src.LedStripRoutine import Strip_Routine
from time import sleep
import src._lib.logger as lg
from src._lib.ConfigToml import ConfigToml
import logging
from src.MqttPublishRoutine import Mqtt_Publish_Routine
from src.MqttSubscribeRoutine import Mqtt_Subscribe_Routine
from src.DataExchange import parse_led_strip, parse_led_strip_HA


if __name__ == "__main__":
    cfg = ConfigToml("/home/pi/_config/config_autorun.toml")
    lg.setup_logging(cfg["paths"]["log"], "auto_", add_date_to_name=True, debug=cfg["debug"])
    logger = logging.getLogger("autorun")
    topics = {"climate": cfg["mqtt"]["topics"]["pub_climate"],
              "cpu": cfg["mqtt"]["topics"]["pub_cpu"],
              "climateHA": cfg["homeassistant"]["pub_climate"],
              "outside": cfg["homeassistant"]["pub_outside"]}
    broker = cfg["mqtt"]["broker"]

    DR = Display_Routine()
    MPR = Mqtt_Publish_Routine(broker, topics, cfg["paths"]["onewire"], cfg["mqtt"]["send_interval"])
    MSR = Mqtt_Subscribe_Routine(broker, cfg["mqtt"]["topics"]["sub_led1"], parse_led_strip)
    HASR = Mqtt_Subscribe_Routine(broker, cfg["homeassistant"]["sub_led1"], parse_led_strip_HA)
    MPR.start()
    MSR.start()
    HASR.start()
    DR.start()

    sleep(5) 
    SR = Strip_Routine(broker, cfg["homeassistant"]["pub_led1"])
    SR.start()

