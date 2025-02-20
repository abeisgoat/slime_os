import time
import gc
import os
from machine import Pin, I2C, UART, SPI
import sdcard

import slime_os.i2c_keyboard as i2c_keyboard
import slime_os.launcher
from slime_os.keycode import Keycode as keycode

from picovision import PicoVision, PEN_P5
from config import config

'''
Intents
-- Intents are used by apps to send signals back to Slime OS for things like
-- closing the app, flipping the render buffer, and swapping apps
'''
INTENT_KILL_APP=[-1]

def INTENT_REPLACE_APP(next_app):
    return [INTENT_KILL_APP[0], next_app]

INTENT_NO_OP=[0]
INTENT_FLIP_BUFFER=[1]

def is_intent(a, b):
    if len(a) == 0 or len(b) == 0:
        return False
    
    return a[0] == b[0]

'''
Expnasions
-- Related to the expansion port
'''

CTRL_EMPTY=-1

CTRL_UART_9600=0
CTRL_UART_STANDARD=CTRL_UART_9600

CTRL_UART_115200=1
CTRL_UART_FAST= CTRL_UART_115200

CTRL_I2C_STANDARD=10
CTRL_I2C_FAST=11

CTRL_NAMES={
   CTRL_EMPTY: "(Empty)",
   CTRL_UART_9600: "UART (9600)",
   CTRL_UART_115200: "UART (115200)",
   CTRL_I2C_STANDARD: "I2C (Standard)",
   CTRL_I2C_FAST: "I2C (Fast)",
}

    
class ExpansionCtrl:
    last_poll=0
    last_ctrl=CTRL_EMPTY
    
    def __init__(self, display):
        self.display = display
    
    def get(self, debug=False):
        voltage = self.display.get_gpu_io_adc_voltage(29)
        
        if debug:
            print(f"The voltage on pin 29 is {voltage:.02f}V")
        
        if 2.3 <= voltage <= 2.6:
            return CTRL_UART_115200
        else:
            return CTRL_EMPTY
    
    def check(self):
        tick = time.ticks_ms()
        
        if (tick-self.last_poll) < 1000:
            return False
        
        self.last_poll = tick
            
        ctrl = self.get()
        
        if self.last_ctrl != ctrl:
            self.last_ctrl = ctrl
            return True
        else:
            return False
        
class Graphics:
    def __init__(self, display):
        self.display = display
        self.dw, self.dh = display.get_bounds()

        self.is_flipped = config["display"]["flipped"]
    
    def set_pen(self, *args, **kwargs):
        self.display.set_pen(*args, **kwargs)
        
    def _adjust_x(self, x, w=0):
        if self.is_flipped:
            return self.dw - w - x
        else:
            return x
        
    def _adjust_y(self, y, h=0):
        if self.is_flipped:
            return self.dh - h - y
        else:
            return y
        
    def rectangle(self, *args):
        x,y,w,h = args
        x = self._adjust_x(x, w)
        y = self._adjust_y(y, h)
        self.display.rectangle(x,y,w,h)
        
    def pixel(self, *args):
        x,y = args
        x = self._adjust_x(x)
        y = self._adjust_y(y)
        self.display.pixel(x,y)
        
    def line(self, *args, **kwargs):
        x1,y1,x2,y2 = args[0:4]
        x1 = self._adjust_x(x1)
        y1 = self._adjust_y(y1)
        x2 = self._adjust_x(x2)
        y2 = self._adjust_y(y2)
        t = args[4] if len(args) == 5 else 1
        self.display.line(x1,y1,x2,y2,t, **kwargs)
        
    def text(self, *args, **kwargs):
        text, x,y = args
        x = self._adjust_x(x)
        y = self._adjust_y(y)
        
        angle = 0
        scale = kwargs["scale"] if "scale" in kwargs else 1
        if self.is_flipped:
            angle = 180
            x -= scale
            y -= 0
        self.display.text(text, x,y, scale=scale, angle=angle)
    
    def measure_text(self, *args, **kwargs):
        return self.display.measure_text(*args, **kwargs)
    
    def update(self):
        return self.display.update()
        


def get_internal_i2c():
    return I2C(1, scl=Pin(7), sda=Pin(6))

def get_expansion_i2c():
    return I2C(1, scl=Pin(1), sda=Pin(0))

def get_expansion_uart():
    return UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
    

def get_applications() -> list[dict[str, str, str]]:
    applications = []
    global app
    
    app_files = os.listdir()
    download_play_app = "/sd/download_play_app.py"
    
    for file in app_files:
        if file.endswith("app.py"):
            applications.append({
                "file": file[:-3],
            })
            
    try:
        os.stat(download_play_app)  # Get file information
        applications.append({
            "file": download_play_app[:-3],
            "temporary": True
        })
    except OSError:
        pass
    
    for app in applications:
        frontmatter = ""
        filename = app["file"] + ".py"
        with open(filename, 'r') as f:
            index = 0
            for line in f.readlines():
                if index == 0:
                    if not line.startswith("'"):
                        print(line)
                        print(f"[APP].MISSING_METADATA {name}")
                        break
                if index > 0:
                    if not line.startswith("'"):
                        frontmatter += line
                    else:
                        break
                index += 1
            f.close()
                
        try:
            exec(frontmatter)
        except SyntaxError:
            print(f"[APP].SYNTAX_ERROR {name}")

    return sorted(applications, key=lambda x: x["name"])


display = PicoVision(PEN_P5, 400, 240)
gfx = Graphics(display)
ctrl = ExpansionCtrl(display)
kbd = i2c_keyboard.Keyboard(get_internal_i2c())

sd_spi = SPI(1, sck=Pin(10, Pin.OUT), mosi=Pin(11, Pin.OUT), miso=Pin(12, Pin.OUT))
sd = sdcard.SDCard(sd_spi, Pin(15))
persist = {}
os.mount(sd, "/sd")
try:
    os.remove("/sd/download_play_app.py")
    print("[sos].temp_file_removed")
except:
    print("[sos].temp_file_missing")
    
def boot(next_app):

    for key,color in config["theme"].items():
        if isinstance(color, tuple):
            config["theme"][key] = display.create_pen(*color)
        #else:
         #   config["theme"][key] = config["theme"][color]
            
    running_app = next_app()
    running_app_instance = None

    while True:
        if running_app:
            if not running_app_instance:
                running_app.setup(display)
                running_app_instance = running_app.run()
            intent = next(running_app_instance)
        else:
            intent = INTENT_FLIP_BUFFER
            
        if is_intent(intent, INTENT_KILL_APP):
            running_app = None
            running_app_instance = None
            print("[SOS].APP_KILLED")
            gc.collect()
            
            next_app = launcher.App
            if len(intent) == 2:
                next_app = __import__(intent[1]["file"]).App
            running_app = next_app()
            
        if is_intent(intent, INTENT_NO_OP):
            pass
        
        
        if is_intent(intent, INTENT_FLIP_BUFFER):
            display.set_pen(config["theme"]["black"])
            display.rectangle(0, 0, gfx.dw, 40)
            display.set_pen(config["theme"]["white"])
            display.line(gfx.dw-12, 40, gfx.dw-12-120, 40)
            display.line(0+12, 40, 0+12+120, 40)
            
            window_title = "SLIMEDECK ZERO"
            
            display.text(window_title, gfx.dw-12-10, 31, -1, 1, 180)
            display.text(free(), 0+12+86, 31, -1, 1, 180)
            display.update()

def prepare_for_launch() -> None:
    for k in locals().keys():
        if k not in ("__name__",
                     "gc"):
            del locals()[k]
    gc.collect()
    
def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = 'MEM USAGE {0:.2f}%'.format(100-(F/T*100))
    if not full: return P
    else : return ('T:{0} F:{1} ({2})'.format(T,F,P))

if __name__ == '__main__':
    boot(slime_os.launcher.App)
