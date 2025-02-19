from system.keycode import Keycode

from machine import Pin, I2C
import system.mcp23017 as mcp23017
i2c = I2C(1, scl=Pin(7), sda=Pin(6)) 
mcp = mcp23017.MCP23017(i2c, 0x20)

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
    "15x13": [Keycode.PERIOD, Keycode.C, Keycode.O, Keycode.M],
    "12x9": Keycode.RIGHT_ARROW,
}

held = {}

for key in kbd_map:
    held[key] = False

rows = {}
used = {}

for key in kbd_map:
    [row, col] = key.split("x")
    
    row = int(row)
    col = int(col)
    
    cols = []
    if row in rows:
        cols = rows[row]
    else:
        rows[row] = cols
        
    cols.append(col)
    
    used[row] = True
    used[col] = True
    

pins = {}
for p in used.keys():
    pins[p] = mcp[p]
    pins[p].input(pull=1)

row_keys = list(rows.keys())
row_keys.sort()

for row in rows:
    rows[row].sort()
            
print("[Keyboard ready!]")

def kbd():
    keys = []
    for pidx in row_keys:
        high_pin = pins[pidx]
        high_pin.output(0)
        for rpidx in rows[pidx]:
            read_pin = pins[rpidx]
            key = "{0}x{1}".format(pidx, rpidx)
            if read_pin.value() == False:
                if not held[key]:
                    keys.append(kbd_map[key])
                held[key] = True
            else:
                held[key] = False
        high_pin.input(pull=1)
    return keys    
