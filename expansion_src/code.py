'''
This is the CircuitPython (not Micropython) source for the Flashlight expansion
'''
import time
import board
import busio
from digitalio import DigitalInOut, Direction

def run(app_data):
  time.sleep(1)

  led = DigitalInOut(board.D8)
  led.direction = Direction.OUTPUT

  uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0.1)

  def send_large_string(uart, data, chunk_size=64, delay=0.15):
    for i in range(0, len(data), chunk_size):
        uart.write(data[i:i+chunk_size])
        time.sleep(delay)

  tick=30
  while True:
    tick += 1
    
    if tick > 30:
      print("sending heartbeat")
      uart.write(bytes("[sos].heartbeat", "ascii"))
      tick=0

    data = uart.readline()  # read up to 32 bytes
    
    if not data is None:
      data_string = (''.join([chr(b) for b in data])).strip()
      if data_string == "[sos].led_on":
        led.value=True
      elif data_string == "[sos].led_off":
        led.value=False
      elif data_string == "[sos].app":
        uart.write(bytes(f"[sos].app:yes:{len(app_data)}", "ascii"))
        send_large_string(uart, app_data)
        uart.write(bytes("[\sos].app:yes\n", "ascii"))
      else:
        print(data_string)

run('''
\'\'\'
app["name"]="Flashlight"
app["id"]="flashlight_app"
app["icon"]="0110000000000000110100000000000011101000000000000111110000000000001111100000000000010111000000000000101110000000000001110111110000000010111000100000000111010000000000011010110100000001110111010000000110111101000000011011101000000000100001000000000000111000"
\'\'\'
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
''')
