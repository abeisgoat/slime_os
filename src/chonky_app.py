'''
app["name"]="Chonky!!"
app["icon"]="0000000000000000000100000000100000101000000101000010010000100100010001111110001001001100001100100101111111111010011111100111111001111111111111101111011111101111101101111110110111011110011110111011011001101101111110011001111101111111111111100001111111111000"
'''
import jpegdec
import time
import system.slime_os as slime_os
import system.i2c_keyboard as keyboard

class App:
    def setup(self, display, colors):
        self.display = display
        j = jpegdec.JPEG(self.display)
        self.display.set_pen(colors["_bg"])
        w, h = display.get_bounds()
        display.rectangle(0, 0, w, h)

        # Open the JPEG file
        j.open_file("chonky_bw.jpg")

        # Decode the JPEG
        j.decode(39, 10, jpegdec.JPEG_SCALE_FULL, dither=True)

    def run(self):
        yield slime_os.INTENT_FLIP_BUFFER
        while True:
            keys = keyboard.kbd()
            len_keys = len(keys)
            if len_keys:
                print(keys)
            if len_keys and keys[0] == 20:
                yield slime_os.INTENT_KILL_APP
                break
            yield slime_os.INTENT_NO_OP
        
    def cleanup(self):
        pass

if __name__ == '__main__':
    __import__("main").boot(App)

