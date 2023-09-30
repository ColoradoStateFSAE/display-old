import board
import neopixel
import time
import math
import multiprocessing as mp
from multiprocessing import Value
import setproctitle

class NeoPixels():
    def __init__(self):
        self.max_brightness = 0.1
        
        self.rpm = mp.Value('d', 0)
        
        self.pixels = neopixel.NeoPixel(board.D18, 30)
        self.pixels.brightness = self.max_brightness
        
        self.last_blink = 0
        self.last_state = True
        
        self.process = mp.Process(target=self.__pixels, daemon=True)
        self.process.start()
        
    def update(self, rpm_input=0):
        self.rpm.value = rpm_input
    
    def __intro(self):
        self.pixels.fill(0)

        for i in range(8):
            self.pixels[i] = (255,255,255)
            self.pixels[15-i] = (255,255,255)
            time.sleep(0.08)
        
        time.sleep(0.5)
            
        i = self.max_brightness
        while(i >= 0):
            i-= .001
            self.pixels.brightness = i
            
        self.pixels.fill(0)
        self.pixels.brightness = self.max_brightness
    
    def __pixels(self):
        setproctitle.setproctitle("display - NeoPixels")
        self.__intro()
    
        while True:
            rpm_range = [7000, 9000, 9500]
            
            percentage = (self.rpm.value - rpm_range[0]) / (rpm_range[1] - rpm_range[0])
            active_pixels = math.ceil(percentage * 6)
            
            if(active_pixels > 0):
                for i in range(active_pixels):
                    if(i < 3):
                        self.pixels[i] = (255, 0, 0)
                        self.pixels[15-i] = (255, 0, 0)
                    elif(i < 6):
                        self.pixels[i] = (0, 0, 255)
                        self.pixels[15-i] = (0, 0, 255)
                    elif(i < 8):
                        self.pixels[i] = (0, 255, 0)
                        self.pixels[15-i] = (0, 255, 0)
                    
                while(self.rpm.value >= rpm_range[2]):
                    self.pixels.brightness = 0
                    time.sleep(0.15)
                    self.pixels.brightness = self.max_brightness
                    time.sleep(0.15)
            else:
                self.pixels.fill(0)
        
    def shutdown(self):
        self.process.kill()