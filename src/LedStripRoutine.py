import threading
import time
from rpi_ws281x import PixelStrip, Color
from datetime import datetime
from .DataExchange import Data
import logging
import paho.mqtt.publish as publish

class Strip_Routine(threading.Thread):
    def __init__(self, broker_ip:str="", pub_topic_state:str=""):
        super(Strip_Routine, self).__init__()
        # LED strip configuration:
        LED_COUNT = 120        # Number of LED pixels.
        LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
        # LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 150  # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        self.COLOR = (Color(52, 225, 235), Color(240, 3, 252)) # color not active clockpi, color active clockpi
        # Create NeoPixel object with appropriate configuration.
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.poll_secs = 1
        self.data = Data()
        # variables for temperature gradient
        self.gradient_colors = ((211, 22, 45), (0, 48, 143)) # fire engine red, dark powder blue
        self.COLOR_Tupel = ((52, 225, 235), (240, 3, 252))
        self.t_max = 30
        self.t_min = 15
        self._logger = logging.getLogger("LED_strip")
        # parameters to publish state for home assistant use
        self.broker_ip = broker_ip
        self.pub_topic_state = pub_topic_state
        if broker_ip == "" or pub_topic_state == "":
            self.publish_state_active = False
        else:
            self.publish_state_active = True

    def run(self):
        mode = ""
        # setting strip to color depending on season
        self.colorWipe(self.strip, self.selectColorSeasonal(), 10)
        self.data.led_strip.color = self.selectColorSeasonal(ret_val_tupel=True)
        publish.single(self.pub_topic_state, self.data.led_strip.to_json(), hostname=self.broker_ip)

        # waiting for changes
        while True:
            if self.data.led_strip.new_data:
                mode = self.data.led_strip.mode
                color = Color(self.data.led_strip.color[0],self.data.led_strip.color[1],self.data.led_strip.color[2])
                self.strip.setBrightness(self.data.led_strip.brightness)   # apply incoming brightness
                if mode in ["wipe", "temperature"]:
                    self.data.led_strip.new_data = False

            match mode:
                case "wipe":
                    self.colorWipe(self.strip, color, 10)
                    if self.publish_state_active:
                        payload=self.data.led_strip.to_json()
                        publish.single(self.pub_topic_state, payload, hostname=self.broker_ip)
                        self._logger.info(payload)
                    mode = ""

                case "rainbow":
                    self.rainbowCycle(self.strip, iterations=10)
                    color = self.selectColorSeasonal()
                    self.data.led_strip.new_data = False
                    mode = "wipe"

                case "chase":
                    self.theaterChase(self.strip, color, iterations=100)
                    self.data.led_strip.new_data = False
                    mode = "wipe"

            # Sleep
            timer = 0
            while (timer < self.poll_secs) and mode in ["", "temperature"]:
                time.sleep(0.01)
                timer += 0.01

        """
        while True:
            print(i)
            self.rainbowCycle(self.strip)
            self.theaterChase(self.strip, Color(127, 127, 127))  # White theater chase
            i += 1
        """

    
    def selectColorSeasonal(self, ret_val_tupel=False):
        today = datetime.now()
        spring_start = datetime(today.year, 3, 20)
        autum_start = datetime(today.year, 9, 22) 

        if (today > spring_start) and (today < autum_start):
            if ret_val_tupel:
                color = self.COLOR_Tupel[0]
            else:
                color = self.COLOR[0]
        else:
            if ret_val_tupel:
                color = self.COLOR_Tupel[1]
            else:
                color = self.COLOR[1]

        return color


    def colorWipe(self, strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)       


    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
        

    #functions which create specific patterns
    def rainbowCycle(self, strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, self.wheel(
                    (int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)    


    def theaterChase(self, strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, color)
                strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i + q, 0)


    def temperature_gradient(self, temperature, color_low = None, color_high = None):
        new_color = []
        if color_low == None:
            color_low = self.gradient_colors[0]

        if color_high == None:
            color_high = self.gradient_colors[1]

        for i in range(0,3):
            m,t = self.determine_slope_equation(color_high[i], color_low[i])
            new_color.append(round(m*temperature+t))
            self._logger.debug(f"{temperature} {color_high[i]}, {color_low[i]}, {m}, {t}, {new_color[-1]}")

        return new_color[0], new_color[1], new_color[2]

         
    def determine_slope_equation(self, color_max, color_min):
        m = (color_max-color_min)/(self.t_max-self.t_min)
        t = color_max-m*self.t_max 
        return m, t
    
