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

    
class Ctrl:
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