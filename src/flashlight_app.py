'''
app["name"]="Flashlight"
app["id"]="flashlight_app"
app["icon"]="0000000000000000000100000000100000101000000101000010010000100100010001111110001001001100001100100101111111111010011111100111111001111111111111101111011111101111101101111110110111011110011110111011011001101101111110011001111101111111111111100001111111111000"
'''
import jpegdec
import time
import slime_os as sos

class App:
    def setup(self, _):
        self.uart = sos.get_expansion_uart()
        
        self.led_on = True
        
    def run(self):
        last_led_on = False
        while True:
            
            if self.led_on != last_led_on:
                sos.gfx.set_pen(sos.config["theme"]["black"])
                sos.gfx.rectangle(0, 0, sos.gfx.dw, sos.gfx.dh)
                sos.gfx.set_pen(sos.config["theme"]["white"])
                message = ""
                if self.led_on:
                    self.uart.write(bytes("[sos].led_on", "ascii"))
                    message = "FLASHLIGHT ON"
                if not self.led_on:
                    self.uart.write(bytes("[sos].led_off", "ascii"))
                    message = "FLASHLIGHT OFF"
                
                sos.gfx.text(message, 20, 20, scale=3)
                sos.gfx.set_pen(sos.config["theme"]["grey"])
                sos.gfx.text("[Press Enter to Toggle]", 20, 50, scale=1)
                yield sos.INTENT_FLIP_BUFFER
                last_led_on = self.led_on
                            
            keys = sos.kbd.get_keys([
                sos.keycode.ENTER,
                sos.keycode.Q
            ])
                
            if keys[sos.keycode.ENTER]:
                self.led_on = not self.led_on
                                
            if keys[sos.keycode.Q]:
                yield sos.INTENT_KILL_APP
                break
            
            yield sos.INTENT_NO_OP
        
    def cleanup(self):
        pass

if __name__ == '__main__':
    sos.boot(App)


