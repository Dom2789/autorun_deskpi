import src._lib.logger as lg
from src._lib.Config import Config
import logging
from src.Mqtt import Mqtt_Routine

def main():
    config = Config("/Users/dom/temp/config_deskpi.txt")

    lg.setup_logging(config.get_item('PWDprot'), "", add_date_to_name=True)
    logger = logging.getLogger("Main")

    logger.info("Hello from autorun-deskpi!")

    MR = Mqtt_Routine(config.get_item("IPbroker"), config.get_item("Topic"), config.get_item("Sendinterval"))
    MR.start()




if __name__ == "__main__":
    main()
