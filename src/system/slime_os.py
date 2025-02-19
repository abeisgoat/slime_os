from machine import Pin, I2C
from os import listdir, stat
import gc

INTENT_KILL_APP=[-1]

def INTENT_REPLACE_APP(next_app):
    return [INTENT_KILL_APP[0], next_app]

INTENT_NO_OP=[0]
INTENT_FLIP_BUFFER=[1]

def is_intent(a, b):
    if len(a) == 0 or len(b) == 0:
        return False
    
    return a[0] == b[0]

def get_i2c():
    return I2C(1, scl=Pin(7), sda=Pin(6))
    

def get_applications() -> list[dict[str, str, str]]:
    applications = []
    global app

    for file in listdir():
        if file.endswith("app.py") and file not in ("main.py", "secrets.py"):
            # Autogen a name, can be overwritten by frontmatter in app file
            name = " ".join([v[:1].upper() + v[1:] for v in file[:-3].split("_")])
            app = {
                "file": file[:-3],
                "name": name
            }
            
            frontmatter = ""
            with open(file, 'r') as f:
                index = 0
                for line in f.readlines():
                    if index == 0:
                        if not line.startswith("'"):
                            print("Missing app metadata")
                            break
                    if index > 0:
                        if not line.startswith("'"):
                            frontmatter += line
                        else:
                            break
                    index += 1
                    
            exec(frontmatter)            
            applications.append(
                app
            )


    return sorted(applications, key=lambda x: x["name"])

def prepare_for_launch() -> None:
    for k in locals().keys():
        if k not in ("__name__",
                     "application_file_to_launch",
                     "gc"):
            del locals()[k]
    gc.collect()
    
def free(full=False):
  gc.collect()
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = 'MEM USAGE {0:.2f}%'.format(100-(F/T*100))
  if not full: return P
  else : return ('T:{0} F:{1} ({2})'.format(T,F,P))
