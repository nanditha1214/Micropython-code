'''
this project has the following features:
  1) it has safety measures to avoid breaking the servo
  2) its settings are all in variables
  3) it auto-centers the servo after it some idle time
  4) it gives a visual indication when the servo is centered- by turning on the led
NOTE:
  THIS CODE IS MADE AND OPTIMPSED FOR RASPBERRY PI PICO, AN ANALOG JOYSTICK AND SG90 SERVO

CONNECTION: 
  SERVO:
    PICO | SERVO
    ------------
    GP16 | SIG/PWM SIGNAL
    VBUS | VCC/POWER
    GND  | GND/GROUND
    
  JOYSTICK:
    PICO | JOYSTICK
    ------------
    ADC1 | X READ/VRX/X READING
    ADC2 | Y READ/VRY/Y READING
    3V3  | VCC/POWER
    GND  | GND/GROUND
 IMPORTS:
 machine and time - you should probabaly know these if wo've used micropython fot atleast a month
 IOAPI - one of my libraries, it is at(https://github.com/nanditha1214/Micropython-code/blob/main/general%20-%20works%20with%20most%20MCUs/my_libs/IOAPI.py)
  '''
import machine
import time
import IOAPI

# Initialize Joystick object from IOAPI with a defined range of 12
jy = IOAPI.Joystick(def_range=12)

# Initialize PWM on pin 16 for controlling the servo motor
servo = machine.PWM(machine.Pin(16))

# Initialize onboard LED (Pin 25) to indicate servo at center position
#pin 25 is connectod to a led on the Raspberry Pi Pico (RP2040 / RP2350)
led_pin_number = 25
led = machine.Pin(led_pin_number, machine.Pin.OUT) 

# Set PWM frequency to 50Hz, typical for servo motors
servo.freq(50)

# Set initial angle for the servo and define control variables
ang = 90  # Start servo at 90 degrees (center position)
speed = 5  # Speed multiplier for servo movement
poll_del = 0.01  # Polling delay in seconds

# tk and tk2 exist only to reduce the angle-printing frequency, so that your ccompyter doesn't hang
#DO NOT EDIT THEM
tk = True  # Toggle flag for timing logic
tk2 = tk  # Secondary toggle flag

# Initialize unchanged reads counter and threshold
unchanged_reads = 0  # Counter for how long the servo angle stays unchanged
old_ang = 90  # Store the last angle of the servo
center_thresh = 5  # Number of unchanged reads before snapping back to center

def de_float(inp):
    """
    Rounds the input to the nearest integer. This is useful for joystick readings
    that may return float values. By rounding them, we can work with integers for angle adjustments.
    """
    return round(inp)

def interval_mapping(x, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another. For example, converts a joystick input
    to an appropriate servo angle or a servo angle to a corresponding PWM duty cycle.

    Parameters:
    x (float): The value to be mapped.
    in_min (float): Minimum of the input range.
    in_max (float): Maximum of the input range.
    out_min (float): Minimum of the output range.
    out_max (float): Maximum of the output range.
    
    Returns:
    float: Mapped value within the new range.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_write(pin, angle):
    """
    Controls the servo motor by mapping the angle to the correct PWM duty cycle.
    
    Parameters:
    pin (machine.Pin): The PWM pin controlling the servo.
    angle (float): The desired servo angle (0 to 180 degrees).
    """
    # Convert the angle to pulse width in milliseconds (0.5ms to 2.5ms)
    pulse_width = interval_mapping(angle, 0, 180, 0.5, 2.5)
    
    # Convert pulse width to PWM duty cycle (0 to 65535)
    duty = int(interval_mapping(pulse_width, 0, 20, 0, 65535))
    
    # Write the PWM duty cycle to control the servo's position
    pin.duty_u16(duty)

def set_limits():
    """
    Ensures the servo angle stays within the allowable range (between 4 and 176 degrees).
    This avoids damaging the servo by preventing it from rotating too far. I've chosen these values so that even if micropython
    skips this function once, it still will still not break the servo.
    """
    global ang  # we declare this to not cause issues(Don't ask me why micropython creates local variables if we don't declare this)
    if ang >= 177:
        ang = 176
    if ang <= 3:
        ang = 4

def center_servo(inp, center=90, inp_boost=20, old_boost=2):
    """
    Smoothly transitions the servo to the desired angle using a weighted average.
    
    Parameters:
        inp (float): The current input value for angle adjustment.
        center (float): The target center value (default is 90 degrees).
        inp_boost (float): Weighting for the current input (default is 20).
        old_boost (float): Weighting for the center position (default is 2).
    
    Returns:
        float: The adjusted angle, smoothly transitioning between input and center.
    """
    return ((inp * inp_boost) + (center * old_boost)) / (inp_boost + old_boost)


def center(inp):
    """
    Resets the servo angle to the center position (90 degrees).
    
    Parameters:
    inp (float): The current angle (unused in this case, simply resets to 90).
    
    Returns:
    float: The centered angle (90 degrees).
    """
    global unchanged_reads
    unchanged_reads = 0  # Reset unchanged reads counter
    return 90  # Return the centered angle

# Main loop to control servo based on joystick input
while True:
    time.sleep(poll_del)  # Wait for polling delay

    # Check if servo has been idle for too long and reset to center
    if unchanged_reads >= center_thresh:
        ang = center(ang)
    
    # Check if the angle hasn't changed and if it's within the center range (80-100 degrees)
    if old_ang == ang and 80 <= ang <= 100:
        unchanged_reads += 1  # Increment unchanged reads counter
    else:
        unchanged_reads = 0  # Reset unchanged reads counter
    
    # Debugging: Print the current angle when both flags are true
    if tk and tk2:
        print(ang)  # Optionally add joystick value here for more context
    
    # Alternate between the flags to reduce print frequency
    if tk:
        tk2 = not tk2
    tk = not tk  # Toggle primary flag

    # Update the angle based on joystick input
    ang += de_float(speed * (jy.read('y')))
    ang = round(center_servo(ang))  # Smoothly adjust the angle using the center_servo function
    
    # Ensure angle stays within the safe range
    set_limits()
    
    # Move the servo to the calculated angle
    servo_write(servo, ang)
    
    # Turn the onboard LED on if the servo is centered (at 90 degrees), off otherwise
    if ang == 90:
        led.on()
    else:
        led.off()
    
    # Store the current angle for the next loop iteration
    old_ang = ang


