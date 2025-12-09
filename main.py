import src._lib.logger as lg
from src._lib.Config import Config
import logging
from src.MqttPublishRoutine import Mqtt_Publish_Routine
from src.MqttSubscribeRoutine import Mqtt_Subscribe_Routine

def main():
    config = Config("/Users/dom/temp/config_deskpi.txt")

    lg.setup_logging(config.get_item('PWDprot'), "", add_date_to_name=True)
    logger = logging.getLogger("Main")

    logger.info("Hello from autorun-deskpi!")

    PR = Mqtt_Publish_Routine(config.get_item("IPbroker"), config.get_item("TopicPub"), config.get_item("Sendinterval"))
    PR.start()

    SR = Mqtt_Subscribe_Routine(config.get_item("IPbroker"), config.get_item("TopicSub"))
    SR.start()


if __name__ == "__main__":
    main()
