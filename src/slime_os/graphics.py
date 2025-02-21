from config import config

class Gfx:
    def __init__(self, display):
        self.display = display
        self.dw, self.dh = display.get_bounds()

        self.is_flipped = config["display"]["flipped"]
    
    def set_pen(self, *args, **kwargs):
        self.display.set_pen(*args, **kwargs)
        
    def _adjust_x(self, x, w=0):
        if self.is_flipped:
            return self.dw - w - x
        else:
            return x
        
    def _adjust_y(self, y, h=0):
        if self.is_flipped:
            return self.dh - h - y
        else:
            return y
        
    def rectangle(self, *args):
        x,y,w,h = args
        x = self._adjust_x(x, w)
        y = self._adjust_y(y, h)
        self.display.rectangle(x,y,w,h)
        
    def pixel(self, *args):
        x,y = args
        x = self._adjust_x(x)
        y = self._adjust_y(y)
        self.display.pixel(x,y)
        
    def line(self, *args, **kwargs):
        x1,y1,x2,y2 = args[0:4]
        x1 = self._adjust_x(x1)
        y1 = self._adjust_y(y1)
        x2 = self._adjust_x(x2)
        y2 = self._adjust_y(y2)
        t = args[4] if len(args) == 5 else 1
        self.display.line(x1,y1,x2,y2,t, **kwargs)
        
    def text(self, *args, **kwargs):
        text, x,y = args
        x = self._adjust_x(x)
        y = self._adjust_y(y)
        
        angle = 0
        scale = kwargs["scale"] if "scale" in kwargs else 1
        if self.is_flipped:
            angle = 180
            x -= scale
            y -= 0
        self.display.text(text, x,y, scale=scale, angle=angle)
    
    def measure_text(self, *args, **kwargs):
        return self.display.measure_text(*args, **kwargs)
    
    def update(self):
        return self.display.update()