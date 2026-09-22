import src._lib.logger as lg
import logging
from src._lib.ConfigToml import ConfigToml
from pprint import pprint

def main():

    cfg = ConfigToml("/Users/dom/temp/autorun_deskpi.toml")
    print(cfg)

    print(cfg["paths"]["log"])
    print(cfg["mqtt"]["topics"]["pub_climate"])
    print(cfg["mqtt"]["topics"]["pub_cpu"])
    print(cfg["homeassistant"]["pub_climate"])
    print(cfg["homeassistant"]["pub_outside"])
    print(cfg["mqtt"]["broker"])
    print(cfg["paths"]["onewire"])
    print(cfg["mqtt"]["send_interval"])
    print(cfg["mqtt"]["topics"]["sub_led1"])
    print(cfg["homeassistant"]["sub_led1"])
    print(cfg["homeassistant"]["pub_led1"])

    lg.setup_logging(cfg["paths"]["log"], "auto_", add_date_to_name=True)
    logger = logging.getLogger("Main")

    logger.info("Hello from autorun-deskpi!")




if __name__ == "__main__":
    main()
