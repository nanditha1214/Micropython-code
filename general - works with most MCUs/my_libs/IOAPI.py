from machine import Pin, ADC
from time import sleep

# IOAPI V1.5 WITH PROPER CODE DOCUMENTATION

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def my_map(x, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another.

    Parameters:
    x (float): The value to be mapped.
    in_min (float): The lower bound of the input range.
    in_max (float): The upper bound of the input range.
    out_min (float): The lower bound of the output range.
    out_max (float): The upper bound of the output range.

    Returns:
    float: The mapped value.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Joystick:
    """
    A class to represent a joystick using two ADC channels.

    Attributes:
    def_range (int): The default range for mapping ADC values to joystick coordinates.
    x_adc (int): The ADC channel number for the X-axis.
    y_adc (int): The ADC channel number for the Y-axis.
    
    Methods:
    read(val, joy_rnge=None): Reads and maps the joystick's X or Y axis to a user-defined range.
    """
    
    def __init__(self, def_range=4, x_adc=1, y_adc=2):
        """
        Initializes the Joystick with default range and ADC channels.
        
        Parameters:
        def_range (int): The default range for the joystick output (-def_range to def_range).
        x_adc (int): The ADC channel for the X-axis.
        y_adc (int): The ADC channel for the Y-axis.
        """
        self.joy_range = def_range  # Default joystick range
        self.joy_x = ADC(x_adc)  # ADC object for the X-axis
        self.joy_y = ADC(y_adc)  # ADC object for the Y-axis

    def read(self, val, joy_rnge=None):
        """
        Reads the joystick position from the X or Y axis and maps the value to a defined range.

        Parameters:
        val (str): 'x' to read the X-axis value, 'y' to read the Y-axis value.
        joy_rnge (int, optional): The range to map the ADC values. Defaults to None, in which case the default joystick range is used.
        
        Returns:
        int: The mapped value for the specified axis (X or Y).
        """
        # Read raw values from the ADC channels
        x_val = self.joy_x.read_u16()  # Raw value for X-axis
        y_val = self.joy_y.read_u16()  # Raw value for Y-axis

        # Map the raw ADC values to the specified or default joystick range
        if joy_rnge is not None:
            x_val = round(my_map(x_val, 0, 65535, -joy_rnge, joy_rnge))
            y_val = round(my_map(y_val, 0, 65535, -joy_rnge, joy_rnge))
        else:
            x_val = round(my_map(x_val, 0, 65535, -self.joy_range, self.joy_range))
            y_val = round(my_map(y_val, 0, 65535, -self.joy_range, self.joy_range))

        # Return the mapped value for the requested axis ('x' or 'y')
        if val == 'x':
            return x_val
        elif val == 'y':
            return y_val
        else:
            return x_val, y_val  # Return both X and Y values if neither axis is specified

# Example of testing the Joystick class (uncomment to use)

'''joystick = Joystick()  # Initialize joystick with default settings
while True:
    print(joystick.read(val='x'), joystick.read(val='y'))  # Print the Y-axis value every 0.1 seconds
    sleep(0.1)'''

