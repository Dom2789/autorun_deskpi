import _lib.logger as lg
from _lib.Config import Config
import logging
from Mqtt import Mqtt_Routine

def main():
    config = Config("/Users/dom/temp/config_deskpi.txt")

    lg.setup_logging(config.get_item('PWDprot'), "", add_date_to_name=True)

    logging.info("Hello from autorun-deskpi!")

    MR = Mqtt_Routine()
    MR.start()




if __name__ == "__main__":
    main()
