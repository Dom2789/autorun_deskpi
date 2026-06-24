#!/usr/bin/python3
from DataExchange import parse_led_strip_HA
from src.DisplayRoutine import Display_Routine
from src.NetworkRoutine import Network_Routine
from src.LedStripRoutine import Strip_Routine
from time import sleep
import src._lib.logger as lg
from src._lib.Config import Config
import logging
from src.MqttPublishRoutine import Mqtt_Publish_Routine
from src.MqttSubscribeRoutine import Mqtt_Subscribe_Routine
from src.DataExchange import parse_led_strip


if __name__ == "__main__":
    config = Config("/home/pi/_config/config_autorun.txt")
    lg.setup_logging(config.get_item('PWDprot'), "auto_", add_date_to_name=True, debug=config.get_bool("DEBUG"))
    logger = logging.getLogger("autorun")
    topics = {"climate": config.get_item("TopicPubClimate"), "cpu": config.get_item("TopicPubCPU")}

    DR = Display_Routine()
    NR = Network_Routine()
    MPR = Mqtt_Publish_Routine(config.get_item("IPbroker"), topics, config.get_item("Sendinterval"))
    MSR = Mqtt_Subscribe_Routine(config.get_item("IPbroker"), config.get_item("TopicSub"), parse_led_strip)
    HASR = Mqtt_Subscribe_Routine(config.get_item("IPbroker"), config.get_item("SubLED1"), parse_led_strip_HA)
    MPR.start()
    MSR.start()
    HASR.start()
    DR.start()
    NR.start()

    sleep(5) 
    SR = Strip_Routine(config.get_item("IPbroker"), config.get_item("PubLED1"))
    SR.start()

