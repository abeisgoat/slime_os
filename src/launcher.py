import gc
import time
import math
import random
from machine import ADC
from os import listdir, stat
from picovision import PicoVision, PEN_P5
from pimoroni import Button
import system.font_microchat as font_microchat
import system.i2c_keyboard as keyboard
import system.slime_os as slime_os

class App:
    def setup(self, display, colors):
        self.display = display
        self.colors = colors


        self.c = 0
        self.step = 1


        # 72 wide, 25 tall

        self.apps = slime_os.get_applications()
        self.str_apps = str(self.apps)

        self.selected_app = 0

        display.set_gpu_io_adc_enable(29, True)
        time.sleep(0.002)


    def run(self):
        while True:
            WIDTH = 400
            HEIGHT = 240
            voltage = self.display.get_gpu_io_adc_voltage(29)
            print(f"The voltage on pin 29 is {voltage:.02f}V")

            if self.selected_app < 0:
                self.selected_app = len(self.apps)-1
            if self.selected_app >= len(self.apps):
                self.selected_app = 0
                
            self.c += self.step
            
            if (self.c > HEIGHT):
                step = -2
            if (self.c < 0):
                step = 2
                
            self.display.set_pen(self.colors["_bg"])
            self.display.rectangle(0, 0, WIDTH, HEIGHT)
            
            self.display.set_pen(self.colors["white"])
            for app_index, app in enumerate(self.apps):

               offset_x = (WIDTH-50) - (app_index * 64)
               offset_y = (HEIGHT-32)
               
               if app_index == self.selected_app:
                   self.display.line(offset_x-32, offset_y-28, offset_x+32, offset_y-28)
                   self.display.line(offset_x-32, offset_y+14, offset_x+32, offset_y+14)
                   self.display.line(offset_x-32, offset_y-28, offset_x-32, offset_y+14)
                   self.display.line(offset_x+32, offset_y-28, offset_x+32, offset_y+14)
                   
               self.display.set_pen(self.colors["white"])
               
               name_width = self.display.measure_text(app["name"], scale=1)
               
               self.display.text(app["name"], offset_x+(name_width//2), offset_y-14, -1, 1, 180)
                                                 
               if "icon" in app:
                   size = -1
                   if len(app["icon"]) == 256:
                       size = 16
                   else:
                       print("Unknown icon length for {0} of {1}".format(app['name'], len(app["icon"])))
                       
                   if size != -1:
                       for bit_index, bit in enumerate(app["icon"]):
                           if bit == "1":
                               y = (bit_index // size) - size//2
                               x = (bit_index % size) - size//2
                               self.display.pixel(offset_x - x, offset_y  - y)
                         
            
            yield slime_os.INTENT_FLIP_BUFFER
            
            keys = []
            len_keys = 0
            while True:
                keys = keyboard.kbd()
                len_keys = len(keys)
                if len_keys:
                    print(keys)
                if len_keys and keys[0] == 79:
                    self.selected_app += 1
                    break
                if len_keys and keys[0] == 80:
                    self.selected_app -= 1
                    break
                if len_keys and keys[0] == 40:
                    yield slime_os.INTENT_REPLACE_APP(self.apps[self.selected_app])
                    break
                yield slime_os.INTENT_NO_OP
            
        
    def cleanup(self):
        pass

    
if __name__ == '__main__':
    __import__("main").boot(App)


