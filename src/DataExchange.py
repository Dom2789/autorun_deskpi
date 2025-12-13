import threading
from dataclasses import dataclass

class Data:
    _instance = None
    _lock = threading.Lock()  # Lock für Thread-Sicherheit

    def __new__(cls):
        with cls._lock:  # Verhindert parallelen Zugriff in Multithreading-Umgebungen
            if cls._instance is None:
                cls._instance = super(Data, cls).__new__(cls)
                cls._instance.data = None  # Gemeinsame Datenvariable
                cls._instance.led_strip = LedStrip(False, 150, "wipe", (255,255,255))
        return cls._instance

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data
    
@dataclass
class LedStrip:
    new_data : bool
    brightness : int
    mode : str
    color : tuple[int, int, int]

    # JSON-representation
    """
    {
    "brightness": 200,
    "mode": "wipe",
    "red": 123, 
    "green": 456, 
    "blue": 789
    }
    """

    """
    {"brightness": 200, "mode": "wipe", "red": 123, "green": 456, "blue": 789}
    """

def parse_led_strip(data:Data, led:dict):
    data.led_strip.new_data = True
    data.led_strip.brightness = led["brightness"]
    data.led_strip.mode = led["mode"]
    data.led_strip.color = (led["red"], led["green"], led["blue"])
    print(data.led_strip.__repr__())