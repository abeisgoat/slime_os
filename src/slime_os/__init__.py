from picovision import PicoVision, PEN_P5
from machine import Pin, I2C, UART, SPI

import time
import gc
import os
import sdcard

import slime_os.i2c_keyboard
import slime_os.launcher

from slime_os.graphics import *
from slime_os.expansion import *

import slime_os.intents as intents
from slime_os.intents import *

from slime_os.keycode import Keycode as keycode

TMP_DOWNLOAD_PLAY_APP = "/sd/download_play_app.py"

def get_internal_i2c():
    return I2C(1, scl=Pin(7), sda=Pin(6))

def get_expansion_i2c():
    return I2C(1, scl=Pin(1), sda=Pin(0))

def get_expansion_uart(baudrate=115200):
    return UART(0, baudrate, tx=Pin(0), rx=Pin(1))
    
def get_sdcard():
    sd_spi = SPI(1, sck=Pin(10, Pin.OUT), mosi=Pin(11, Pin.OUT), miso=Pin(12, Pin.OUT))
    return sdcard.SDCard(sd_spi, Pin(15))

def get_applications() -> list[dict[str, str, str]]:
    applications = []
    global app
    
    app_files = os.listdir()
    download_play_app = TMP_DOWNLOAD_PLAY_APP
    
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
gfx = Gfx(display)
ctrl = Ctrl(display)
kbd = None

if config["input"]["keyboard"] == "i2c":
    kbd = slime_os.i2c_keyboard.Keyboard(get_internal_i2c())

sd = get_sdcard()
persist = {}
os.mount(sd, "/sd")
try:
    os.remove(TMP_DOWNLOAD_PLAY_APP)
    print("[sos].temp_file_removed")
except:
    print("[sos].temp_file_missing")
    
def boot(next_app):

    for key,color in config["theme"].items():
        if isinstance(color, tuple):
            config["theme"][key] = display.create_pen(*color)
            
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
