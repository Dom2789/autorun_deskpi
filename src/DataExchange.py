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
    if led["red"]<0 or led["red"]>255:
        return "Value for red out of bounds!"
    
    if led["green"]<0 or led["green"]>255:
        return "Value for green out of bounds!"
    
    if led["blue"]<0 or led["blue"]>255:
        return "Value for blue out of bounds!"
    
    if led["brightness"]<0 or led["brightness"]>255:
        return "Value for brightness out of bounds!"
    
    if led["mode"] not in ["wipe", "rainbow", "chase"]:
        return f"Invalid mode '{led["mode"]}'!"
    
    data.led_strip.new_data = True
    data.led_strip.brightness = led["brightness"]
    data.led_strip.mode = led["mode"]
    data.led_strip.color = (led["red"], led["green"], led["blue"])

    return None