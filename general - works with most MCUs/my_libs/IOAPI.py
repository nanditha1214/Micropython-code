
'''IOAPI v1
'''

from machine import Pin, ADC
import machine
from time import sleep

def my_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min





class Joystick:
    def __init__(self, def_range=8):
        self.joy_range = def_range
        self.joy_x = ADC(1)
        self.joy_y = ADC(2)
        
    def read(self, val, joy_rnge=None):
        x_val = self.joy_x.read_u16()  # Read X-axis
        y_val = self.joy_y.read_u16()  # Read Y-axis
        
        if joy_rnge is not None:
            x_val = round(my_map(x_val, 0, 65535, -joy_rnge, joy_rnge))
            y_val = round(my_map(y_val, 0, 65535, -joy_rnge, joy_rnge))
        else:
            x_val = round(my_map(x_val, 0, 65535, -self.joy_range, self.joy_range))
            y_val = round(my_map(y_val, 0, 65535, -self.joy_range, self.joy_range))
        
        if val == 'x':
            return x_val
        elif val == 'y':
            return y_val
        else:
            return x_val, y_val

# Uncomment this section to test the joystick class

'''joystick = Joystick()
while True:
    print(joystick.(val='y'))
    sleep(0.1)
'''

