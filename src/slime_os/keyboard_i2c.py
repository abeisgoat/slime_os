from slime_os.keycode import Keycode
from machine import Pin, I2C
import slime_os.mcp23017 as mcp23017

kbd_map = {
    "13x12": Keycode.Q,
    "10x4": Keycode.W,
    "9x4": Keycode.E,
    "4x1": Keycode.T,
    "4x2": Keycode.R,
    "4x0": Keycode.Y,
    "15x4": Keycode.U,
    "14x4": Keycode.I,
    "13x4": Keycode.O,
    "10x9": Keycode.P,
    "12x4": Keycode.UP_ARROW,
    "10x2": Keycode.A,
    "10x1": Keycode.S,
    "10x0": Keycode.D,
    "15x10": Keycode.F,
    "14x10": Keycode.G,
    "13x10": Keycode.H,
    "9x2": Keycode.J,
    "9x1": Keycode.K,
    "9x0": Keycode.L,
    "15x9": Keycode.BACKSPACE,
    "12x2": Keycode.DOWN_ARROW,
    "14x9": Keycode.TAB,
    "13x9": Keycode.Z,
    "2x1": Keycode.X,
    "2x0": Keycode.C,
    "15x2": Keycode.V,
    "14x2": Keycode.B,
    "13x2": Keycode.N,
    "1x0": Keycode.M,
    "15x1": Keycode.KEYPAD_FORWARD_SLASH,
    "14x1": Keycode.ENTER,
    "12x10": Keycode.LEFT_ARROW,
    #weird shift // any 11
    #weird alt // any 3 alt
    "13x1": 206, #"@",
    "15x0": 203,
    "14x0": Keycode.SPACE,
    "13x0": Keycode.COMMA,
    "15x14": Keycode.PERIOD,
    #"15x13": [Keycode.PERIOD, Keycode.C, Keycode.O, Keycode.M],
    "12x9": Keycode.RIGHT_ARROW,
}

kbd_map_inv = {}

for key,value in kbd_map.items():
    r,c = key.split("x")
    kbd_map_inv[value] = [int(r), int(c)]


class Keyboard:
    def __init__(self, i2c):
        self.is_ready = False
        try:
            mcp = mcp23017.MCP23017(i2c, 0x20)
            self.is_ready=True
        except OSError as e:
            print("[KBD].error:", e)
            self.is_ready=False
            
        self.held = {}

        for key in kbd_map:
            self.held[key] = False

        self.rows = {}
        used = {}

        for key in kbd_map:
            [row, col] = key.split("x")
            
            row = int(row)
            col = int(col)
            
            cols = []
            if row in self.rows:
                cols = self.rows[row]
            else:
                self.rows[row] = cols
                
            cols.append(col)
            
            used[row] = True
            used[col] = True
            
        if self.is_ready:
            self.pins = {}
            for p in used.keys():
                self.pins[p] = mcp[p]
                self.pins[p].input(pull=1)

            self.row_keys = list(self.rows.keys())
            self.row_keys.sort()

            for row in self.rows:
                self.rows[row].sort()
                        
            print("[KBD].ready")
        else:
            print("[KBD].not_ready")
            
    def get_key(self, key):
        row,col = kbd_map_inv[key]
        
        high_pin = self.pins[row]
        high_pin.output(0)

        read_pin = self.pins[col]
        
        key = "{0}x{1}".format(row, col)
        
        pressed = False
        
        if read_pin.value() == False:
            if not self.held[key]:
                pressed = True
            self.held[key] = True
        else:
            self.held[key] = False
            
        high_pin.input(pull=1)
        return pressed
    
    def get_keys(self, keys):
        results = {}
        
        for key in keys:
            results[key] = self.get_key(key)
        
        return results
    
    def get_all(self):
        keys = []
        
        if not self.is_ready:
            return keys
        
        for pidx in self.row_keys:
            high_pin = self.pins[pidx]
            high_pin.output(0)
            for rpidx in self.rows[pidx]:
                read_pin = self.pins[rpidx]
                key = "{0}x{1}".format(pidx, rpidx)
                if read_pin.value() == False:
                    if not self.held[key]:
                        keys.append(kbd_map[key])
                    self.held[key] = True
                else:
                    self.held[key] = False
            high_pin.input(pull=1)
        return keys    
