import gc
import time
import math
import random
from machine import ADC
import os
from picovision import PicoVision, PEN_P5
from pimoroni import Button
import slime_os as sos


def gfx_expansion_modal(gfx, ctrl_name, attempts, success):
        mw = 199
        mh = 54
        cx = (gfx.dw-mw)//2
        cy = int((gfx.dh-mh)/2.5)
        padding = 6
        
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.rectangle(cx+padding, cy+padding, mw, mh)
        gfx.set_pen(sos.config["theme"]["white"])
        gfx.rectangle(cx, cy, mw, mh)
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.text("Expansion installed", cx+padding, cy+7, scale=1)
        gfx.line(cx+3, cy+18, cx+mw-3, cy+18)
        
        gfx.set_pen(sos.config["theme"]["grey"])
        ctrl_name_width = gfx.measure_text(ctrl_name, scale=1)
        gfx.text(ctrl_name, cx+mw-padding-ctrl_name_width, cy+7, scale=1)
        
        status = "Attemping to handshake..."
        if success == False:
            status = "Hankshake failure."
        if success == True:
            status = "Handshake success."
        gfx.text(status, cx+padding, cy+24)
        
        gspacing = 3
        gh = 14
        gw = (mw-padding*2-gspacing*4)//5
        gy = cy+35
        
        gfx.set_pen(sos.config["theme"]["black"])
        for i in range(0, 5):
            gfx.rectangle(cx+padding+(i*(gw+gspacing)), gy, gw, gh)
            
        gfx.set_pen(sos.config["theme"]["white"])
        
        for i in range(0, 5):
            gfx.rectangle(cx+padding+1+(i*(gw+gspacing)), gy+1, gw-2, gh-2)
            
        gfx.set_pen(sos.config["theme"]["yellow"])
        if success==False:
            gfx.set_pen(sos.config["theme"]["red"])
        for i in range(0, attempts):
            if i == attempts-1 and success:
                gfx.set_pen(sos.config["theme"]["green"])
            gfx.rectangle(cx+padding+1+(i*(gw+gspacing)), gy+1, gw-2, gh-2)
            

def gfx_download_modal(gfx, ctrl_name, percent, success):
        mw = 199
        mh = 54
        cx = (gfx.dw-mw)//2
        cy = int((gfx.dh-mh)/2.5)
        padding = 6
        
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.rectangle(cx+padding, cy+padding, mw, mh)
        gfx.set_pen(sos.config["theme"]["white"])
        gfx.rectangle(cx, cy, mw, mh)
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.text("Expansion App", cx+padding, cy+7, scale=1)
        gfx.line(cx+3, cy+18, cx+mw-3, cy+18)
        
        gfx.set_pen(sos.config["theme"]["grey"])
        ctrl_name_width = gfx.measure_text(ctrl_name, scale=1)
        gfx.text(ctrl_name, cx+mw-padding-ctrl_name_width, cy+7, scale=1)
        
        status = "Attemping to sync app"
        gfx.text(status, cx+padding, cy+24)
        
        gfx.set_pen(sos.config["theme"]["yellow"])
        
        if success:
            gfx.set_pen(sos.config["theme"]["green"])
            
        gh = 14
        gy = cy+35
        gfx.rectangle(cx+padding, gy, int((mw-padding*2)*percent), gh)
        
        if success:
            gfx.set_pen(sos.config["theme"]["white"])
            status = "App installed."
            gfx.text(status, cx+padding+padding, gy+5)
    

class App:
    def setup(self, display):
        self.display = display

        self.do_get_apps()
        if not "launcher" in sos.persist:
            sos.persist["launcher"] = {
                "selected_app": 0,
                "welcome": False
                }

        display.set_gpu_io_adc_enable(29, True)
        time.sleep(0.002)

    def do_get_apps(self):
        self.apps = sos.get_applications()
        self.str_apps = str(self.apps)
        
    def do_uart_expansion(self):
        ctrl = sos.ctrl
        gfx = sos.gfx
        ctrl_value = ctrl.get()
        
        uart = sos.get_expansion_uart()
        
        accepted = False
        for i in range(0, 6):
            time.sleep(1)
            print(f"[EXP].HANDSHAKE_WAITING: {i}")
            if i != 5:
                gfx_expansion_modal(sos.gfx, sos.CTRL_NAMES[ctrl_value], i, None)
                yield sos.INTENT_FLIP_BUFFER
            uart_data = uart.readline()
            
            if uart_data:
                data_string = ''.join([chr(b) for b in uart_data])
                print(f"> {data_string}")
                if data_string.strip()[0:5] == "[sos]":
                    print("[EXP].HANDSHAKE_ACCEPTED")
                    accepted = True
                    gfx_expansion_modal(gfx, sos.CTRL_NAMES[ctrl_value], i, True)
                    yield sos.INTENT_FLIP_BUFFER
                    break
            else:
                print("> [no data]")
                
        if not accepted:
            gfx_expansion_modal(gfx, sos.CTRL_NAMES[ctrl_value], i, False)
            yield sos.INTENT_FLIP_BUFFER
            print("[EXP].HANDSHAKE_REJECTED")
                    

    def do_menu(self):
        gfx = sos.gfx
        if  sos.persist["launcher"]["selected_app"] < 0:
            sos.persist["launcher"]["selected_app"] = len(self.apps)-1
        if sos.persist["launcher"]["selected_app"] >= len(self.apps):
            sos.persist["launcher"]["selected_app"] = 0
            
        self.display.set_pen(sos.config["theme"]["blue"])
        self.display.rectangle(0, 0, sos.gfx.dw, sos.gfx.dh)
        
        self.display.set_pen(sos.config["theme"]["white"])
        for app_index, app in enumerate(self.apps):

           offset_x = 50 + (app_index * 64)
           offset_y = 32
           
           is_temporary = "temporary" in app and app["temporary"] == True
           is_selected = app_index == sos.persist["launcher"]["selected_app"]
           show_outline = is_selected
           
           if show_outline:
               sos.gfx.line(offset_x+31, offset_y+28, offset_x-32, offset_y+28,3)
               sos.gfx.line(offset_x+31, offset_y-14, offset_x-31, offset_y-14)
               sos.gfx.line(offset_x+31, offset_y+28, offset_x+31, offset_y-15)
               sos.gfx.line(offset_x-31, offset_y+28, offset_x-31, offset_y-15)
             
        
           self.display.set_pen(sos.config["theme"]["white"])
           if is_temporary:
               for i in range(-2, 4):
                   dx = (i*6) - 6
                   sos.gfx.line(offset_x+dx, offset_y+23, offset_x+dx+4, offset_y+23, 2)
               
           '''if is_temporary and not is_selected:
               
               for i in range(-2, 4):
                   dy = 4+i*7
                   sos.gfx.line(offset_x+34, offset_y+dy, offset_x-35, offset_y+dy, 3)
               for i in range(-4, 4):
                   dx = 4+i*8
                   sos.gfx.line(offset_x+dx, offset_y-16, offset_x+dx, offset_y+30, 3)
               #sos.gfx.line(offset_x-32, offset_y+28, offset_x-32, offset_y-15, 5)'''
  
               
           self.display.set_pen(sos.config["theme"]["white"])
           
           name_width = self.display.measure_text(app["name"], scale=1)
           
           sos.gfx.text(app["name"], offset_x-1-(name_width//2), offset_y+14)
                                             
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
                           sos.gfx.pixel(offset_x + x, offset_y  + y)

    def do_download_play(self):
        uart = sos.get_expansion_uart()
        uart.write(bytes("[sos].app", "ascii"))
        time.sleep(0.1)
        
        fails = 0
        line = ''
        length = 1
        size = 0
        
        tmp_file = "/sd/download_play_app.py"
        with open(tmp_file, "w") as f:
            while True:
                uart_data = uart.read(128)
                
                if uart_data is not None:
                    fails = 0
                    for b in uart_data:
                        char = chr(b)
                        line += char
                        
                        if char == "\n":
                            
                            if line[0:14] == "[sos].app:yes:":
                                size = int(line[14:])
                                print("[EXP].APP_DOWNLOAD_START")
                                yield (-size + length)
                            elif line[0:14] == "[\sos].app:yes":
                                yield (-size + length)
                                print(f"[EXP].APP_DOWNLOAD_END:{length} of {size}")
                                break
                            else:
                                length += len(line)
                                f.write(line)
                                yield (-size + length)
                            line = ""
                            
                else:
                    fails += 1
                    if (fails > 10000):
                        break
                    
            f.close()
    def do_welcome(self, cursor=0):
        if not sos.persist["launcher"]["welcome"]:
            sos.gfx_alert_modal(sos.gfx, "Welcome to Slime OS", "[MESSAGE]", "Stay awhile, tinker, hack, have fun!", cursor)
            
    def run(self):
        last_selected_app = -1
        while True:
            if sos.ctrl.check():
                ctrl_value = sos.ctrl.get()
                ctrl_name = sos.CTRL_NAMES[ctrl_value]
                print(f"[EXP].CHANGE: {ctrl_name}")
                if ctrl_value == sos.CTRL_EMPTY:
                    try:
                        os.remove("/sd/download_play_app.py")
                        print("[sos].temp_file_removed")
                    except:
                        print("[sos].temp_file_missing")
                
                if ctrl_value == sos.CTRL_UART_115200:
                    do = self.do_uart_expansion()
                    last_selected_app = sos.persist["launcher"]["selected_app"]
                    
                    while do:
                        self.do_menu()
                        try:
                            yield next(do)
                        except StopIteration:
                            time.sleep(3)
                            break
                        
                    do = self.do_download_play()
                    size = -next(do)
                    while do:
                        try:
                            remaining = next(do)
                            percent = 1-(-remaining/size)
                            gfx_download_modal(sos.gfx, ctrl_name, percent, remaining == 0)
                            yield sos.INTENT_FLIP_BUFFER
                        except StopIteration:
                            time.sleep(3)
                            break
                    
                self.do_get_apps()
                self.do_menu()
                yield sos.INTENT_FLIP_BUFFER
            
            if last_selected_app != sos.persist["launcher"]["selected_app"]:
                self.do_menu()
                self.do_welcome()
                yield sos.INTENT_FLIP_BUFFER
                last_selected_app = sos.persist["launcher"]["selected_app"]
                
            keys = sos.kbd.get_keys([
                sos.keycode.ENTER,
                sos.keycode.LEFT_ARROW,
                sos.keycode.RIGHT_ARROW
            ])
            
            if keys[sos.keycode.LEFT_ARROW]:
                sos.persist["launcher"]["selected_app"] -= 1
            if keys[sos.keycode.RIGHT_ARROW]:
                sos.persist["launcher"]["selected_app"] += 1
            if keys[sos.keycode.ENTER]:
                if not sos.persist["launcher"]["welcome"]:
                    self.do_menu()
                    self.do_welcome(1)
                    yield sos.INTENT_FLIP_BUFFER
                    time.sleep(0.01)
                    self.do_menu()
                    self.do_welcome(0)
                    yield sos.INTENT_FLIP_BUFFER
                    time.sleep(0.01)
                    self.do_menu()
                    self.do_welcome(1)
                    sos.persist["launcher"]["welcome"] = True
                    self.do_menu()
                    yield sos.INTENT_FLIP_BUFFER
                else:
                    yield sos.INTENT_REPLACE_APP(
                        self.apps[sos.persist["launcher"]["selected_app"]]
                        )
                    break
            
            yield sos.INTENT_NO_OP
            
        
    def cleanup(self):
        pass

    
if __name__ == '__main__':
    __import__("slime_os").boot(App)