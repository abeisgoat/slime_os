import time
import gc

from picovision import PicoVision, PEN_P5
import launcher
import system.slime_os as slime_os

def boot(next_app):
    WIDTH = 400
    HEIGHT = 240
    display = PicoVision(PEN_P5, WIDTH, HEIGHT)

    colors = {
        "blue": display.create_pen(0, 39, 65),
        "red": display.create_pen(255, 0, 0),
        "green": display.create_pen(0, 255, 0),
        "black":  display.create_pen(0, 0, 0),
        "white": display.create_pen(255, 255, 255)
    }
    colors["_bg"] = colors["blue"]

    running_app = next_app()
    running_app_instance = None

    fps = 0
    visual_fps = 0

    t = time.ticks_ms()
    while True:
        if running_app:
            if not running_app_instance:
                running_app.setup(display, colors)
                running_app_instance = running_app.run()
            intent = next(running_app_instance)
        else:
            intent = slime_os.INTENT_FLIP_BUFFER
            print(slime_os.free(), visual_fps)
                    
        if slime_os.is_intent(intent, slime_os.INTENT_KILL_APP):
            running_app = None
            running_app_instance = None
            print("Running app killed")
            gc.collect()
            
            next_app = launcher.App
            if len(intent) == 2:
                next_app = __import__(intent[1]["file"]).App
            running_app = next_app()
            
        if slime_os.is_intent(intent, slime_os.INTENT_NO_OP):
            pass
        
        if slime_os.is_intent(intent, slime_os.INTENT_FLIP_BUFFER):
            display.set_pen(colors["black"])
            display.rectangle(0, 0, WIDTH, 40)
            display.set_pen(colors["white"])
            display.line(WIDTH-12, 40, WIDTH-12-120, 40)
            display.line(0+12, 40, 0+12+120, 40)
            display.text("SLIMEDECK ZERO", WIDTH-12-10, 31, -1, 1, 180)
            #fps_text = "FPS: {0}".format(visual_fps)
            display.text(slime_os.free(), 0+12+86, 31, -1, 1, 180)
            display.update()
            
        if (time.ticks_ms() > (t+1000)):
            visual_fps = fps
            t = time.ticks_ms()
            fps = 0
                    
        fps += 1
    
if __name__ == '__main__':
    boot(launcher.App)