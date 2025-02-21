'''
Intents
-- Intents are used by apps to send signals back to Slime OS for things like
-- closing the app, flipping the render buffer, and swapping apps
'''
INTENT_KILL_APP=[-1]

def INTENT_REPLACE_APP(next_app):
    return [INTENT_KILL_APP[0], next_app]

INTENT_NO_OP=[0]
INTENT_FLIP_BUFFER=[1]

def is_intent(a, b):
    if len(a) == 0 or len(b) == 0:
        return False
    
    return a[0] == b[0]