#!/usr/bin/python3
from src.DisplayRoutine import Display_Routine
from src.NetworkRoutine import Network_Routine
from src.LedStripRoutine import Strip_Routine
from src.Mqtt import Mqtt_Routine
from time import sleep
from src._lib.Config import Config


if __name__ == "__main__":
    config = Config("/home/pi/_config/config_autorun.txt")
  
    DR = Display_Routine()
    NR = Network_Routine()
    MR = Mqtt_Routine(config.get_item("IPbroker"), config.get_item("topic"))
    DR.start()
    NR.start()
    MR.start()

    sleep(5) 
    SR = Strip_Routine() 
    SR.start()

