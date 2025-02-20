'''
app["name"]="Serial"
app["id"]="serial_app"
app["icon"]="0000000000000000000100000000100000101000000101000010010000100100010001111110001001001100001100100101111111111010011111100111111001111111111111101111011111101111101101111110110111011110011110111011011001101101111110011001111101111111111111100001111111111000"
'''
import jpegdec
import time
import slime_os as sos

class App:
    def setup(self, display):
        # 72 wide, 25 tall
        pass


    def run(self):
        offset = 0
        while True:
            sos.gfx.set_pen(sos.config["theme"]["blue"])
            sos.gfx.rectangle(0, 0, sos.gfx.dw, sos.gfx.dh)
            sos.gfx.set_pen(sos.config["theme"]["white"])
            lines = []
            for i in range(0+offset, 26+offset):
                lines.append(str(i) + ": " + "X" * 70)
                
            sos.gfx.text("\n".join(lines), 10, 10)
            offset += 1
            keys = sos.kbd.get_keys([sos.keycode.Q])
            if keys[sos.keycode.Q]:
                yield sos.INTENT_KILL_APP
                break
            yield sos.INTENT_FLIP_BUFFER
        
    def cleanup(self):
        pass

if __name__ == '__main__':
    sos.boot(App)


