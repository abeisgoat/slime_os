'''
app["name"]="I2C Scan"
app["icon"]="0000000000000000000011010000000000000000000000000001111010000000000111101000000000011110101100000001111010111000000111101001110000011110100011100001111010000110000000000000011000001101000001100000000000001110000000000001110000111111010110000001111010110000"
'''
import random
import system.i2c_keyboard as keyboard
import system.slime_os as slime_os

class App:
    def setup(self, display, colors):
        self.known_addresses = {
            "0D": "PicoVision GPU",
            "20": "Keyboard GPIO Expander"
        }
        self.cols = "0123456789ABCDEF"
        self.rows = "01234567"
    
        self.display = display
        self.colors = colors
        self.display.set_pen(self.colors["_bg"])
        self.cursor = {"x": 0, "y": 0}
        w, h = display.get_bounds()
        display.rectangle(0, 0, w, h)
        
        self.output = "I2C Scan\n-----------------------------\n"
        self.output += 'Scan i2c bus...\n'
        self.devices = {}

        
        for device in slime_os.get_i2c().scan():
            addr = f'{device:02X}'
            
            if addr in self.known_addresses:
                name = self.known_addresses[addr]
            else:
                name = "Unknown Device"
                
            device = {
              "addr": addr,
              "name": name,
              "x": self.cols.find(addr[1]),
              "y": self.rows.find(addr[0])
            }
            
            
            self.devices[f'{device["x"]}x{device["y"]}'] = device


    def run(self):        
        while True:
            
            if self.cursor["x"] < 0:
                self.cursor["x"] = 15
            if self.cursor["x"] > 15:
                self.cursor["x"] = 0
                
            if self.cursor["y"] < 0:
                self.cursor["y"] = 7
            if self.cursor["y"] > 7:
                self.cursor["y"] = 0
                
            self.display.set_pen(self.colors["_bg"])
            w, h = self.display.get_bounds()
            self.display.rectangle(0, 0, w, h)
            self.display.set_pen(self.colors["white"])
            
            y_offset = 26
            x_offset = 36
            
            for col_index, col in enumerate(self.cols):
                self.display.text(col, 400-x_offset-((col_index+1)*20), 240-y_offset, -1, 1, 180)
                
            #f'{device:x}'
            #print()
            selected_device = "No Device selected."
            for row_index, row in enumerate(self.rows):
                y = 240-y_offset-((row_index+1)*16)
                self.display.set_pen(self.colors["white"])
                self.display.text(row, 400-x_offset, y, -1, 1, 180)
                for col_index in range(1, 17):
                    table_x = col_index-1
                    table_y = row_index
                    pos = f'{table_x}x{table_y}'
                    text = "--"
                    
                    x = 400-x_offset-(col_index*20)
                    
                    is_cursor = self.cursor["x"] == table_x and self.cursor["y"] == table_y
                    
                    if is_cursor:
                        self.display.set_pen(self.colors["black"])
                        self.display.rectangle(x-12, y-8, 16, 11)
                    
                    if pos in self.devices:
                        text = self.devices[pos]["addr"]
                        self.display.set_pen(self.colors["white"])
                        if is_cursor:
                            selected_device = f'Device: {self.devices[pos]["name"]}'
                        if not is_cursor:
                            self.display.rectangle(x-12, y-8, 16, 11)
                            self.display.set_pen(self.colors["black"])
                    else:
                        self.display.set_pen(self.colors["white"])
                        
                    self.display.text(text, x, y, -1, 1, 180)
                    
            self.display.line(400-x_offset, 240-y_offset-144, x_offset, 240-y_offset-144)
            self.display.text(selected_device, 400-x_offset, 240-y_offset-152, -1, 1, 180)
            
            yield slime_os.INTENT_FLIP_BUFFER
            while True:
                keys = keyboard.kbd()
                len_keys = len(keys)
                if len_keys:
                    print(keys)
                    
                if len_keys and keys[0] == 79:
                    self.cursor["x"] += 1
                    break

                if len_keys and keys[0] == 80:
                    self.cursor["x"] -= 1
                    break
                
                if len_keys and keys[0] == 81:
                    self.cursor["y"] += 1
                    break

                if len_keys and keys[0] == 82:
                    self.cursor["y"] -= 1
                    break
                    
                if len_keys and keys[0] == 20:
                    yield slime_os.INTENT_KILL_APP
                
  
        
    def cleanup(self):
        pass


if __name__ == '__main__':
    __import__("main").boot(App)
