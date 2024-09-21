# This code is heavily interlinked, so it won't work if you take any segment out of it.
import neopixel
import time
import machine
import network
import ntptime
raise ValueError('fill details in lines 10-14, and comment out line 7')
'''Note: pix 12 is 30 sec mark , pix 18 is 45 sec mark...'''
# Settings
wifi_SSID = 'ssid'
wifi_PWD  = 'password'
time_off = 5.5 * 3600  # UTC offset in seconds
bg_col = (4, 2, 3)     # Background color
np_pin = 1             # NeoPixel GPIO pin
#dev feature
ck_type = 24           # Clock type: 12 or 24-hour format

# Neopixel setup
pin = machine.Pin(np_pin)   # Set GPIO to output to drive NeoPixels
np = neopixel.NeoPixel(pin, 24)   # Create NeoPixel driver on GPIO0 for 24 pixels

# Network setup
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Try connecting to WiFi and syncing time
try:
    if not sta.isconnected():
        sta.connect(wifi_SSID, wifi_PWD)
        while not sta.isconnected():
            pass
    print('Connection successful')
    
    try:
        ntptime.settime()  # Sync time from NTP server
        print("Time synchronized successfully")
    except Exception as e:
        print("Error syncing time:", e)
        actual_time = (2023, 9, 12, 1, 56, 0, 0, 0)  # Default time if NTP fails
except Exception as e:
    print("WiFi connection failed, setting default time")
    actual_time = (2023, 9, 12, 1, 56, 0, 0, 0)  # Default time if no WiFi

# Timezone offset
UTC_OFFSET = int(time_off)

# Helper functions
def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - out_min) + out_min

def get_pix_value(tm, ip=60, ct=24):
    return round(map_value(tm, 0, ip, 0, ct))

def write(r, g, b, i):
    np[i] = (r, g, b)  # Set the pixel color

def orient(inp):
    return (inp + 12) % 24  # Always map the position to the 24-pixel range

def get_sec():
    seconds = actual_time[5]
    return orient(get_pix_value(tm=seconds, ip=60, ct=24))  # Always use 24 pixels for seconds

def get_min():
    minutes = actual_time[4]
    return orient(get_pix_value(tm=minutes, ip=60, ct=24))  # Always use 24 pixels for minutes

def get_hr():
    hour = actual_time[3]
    
    if ck_type == 12:
        if hour == 0:
            hour = 12  # Midnight becomes 12 AM
        elif hour > 12:
            hour -= 12  # Convert 13-23 to 1-11 for PM
    
    pixel_range = 12 if ck_type == 12 else 24
    return orient(get_pix_value(hour, ip=24))#, ct=pixel_range))

def f_to_i(a, b, c):
    return int(a), int(b), int(c)

def update_color(r, g, b, i):
    '''if ck_type == 12 and actual_time[3] >= 12:
        r, g, b = f_to_i(r/2, g/2, b/2)  # Dim colors by 50% for PM'''# work in progress
    
    tup = np[i]
    nr = r if r != '-' else tup[0]
    ng = g if g != '-' else tup[1]
    nb = b if b != '-' else tup[2]
    
    write(nr, ng, nb, i)

# Main loop
while True:
    actual_time = time.localtime(time.time() + UTC_OFFSET)
    print(actual_time)
    
    np.fill(bg_col)  # Fill background color
    
    # Update NeoPixels for second, minute, and hour
    update_color(255, '-', '-', get_sec())   # Red for seconds
    update_color('-', 255, '-', get_min())   # Green for minutes
    update_color('-', '-', 255, get_hr())    # Blue for hours
    
    np.write()  # Refresh the LEDs
    time.sleep(0.5)
