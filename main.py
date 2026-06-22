import src._lib.logger as lg
import logging
from src.MqttSubscribeRoutine import Mqtt_Subscribe_Routine
from src.DataExchange import LedStrip, parse_led_strip_HA


def main():


    lg.setup_logging("/home/dom/temp/", "auto_", add_date_to_name=True)
    logger = logging.getLogger("Main")

    logger.info("Hello from autorun-deskpi!")

    mqtt()


def mqtt():
    #PR = Mqtt_Publish_Routine(config.get_item("IPbroker"), config.get_item("TopicPub"), config.get_item("Sendinterval"))
    #PR.start()

    SR = Mqtt_Subscribe_Routine("192.168.178.100", "led/living/1/set", parse_led_strip_HA)
    SR.start()






if __name__ == "__main__":
    main()
