import neopixel
import time
import machine
import network
import ntptime
from random import randint # time-pass

# Settings

wifi_SSID = ['ssid0','ssid1']  #wifi ssid(s)
wifi_PWD  = ['pwd0','pwd1']    #wifi pwd(s)
wifi_id = 0                    #which ssid/pwd to use(follow python array rules whie entering a value)
time_off = 5.5 * 3600  # UTC offset in seconds
bg_col = (3, 1, 2)     # Background color
np_pin = 1             # NeoPixel pin
ck_type = 12           # Clock type: 12 or 24-hour format

# Neopixel setup
pin = machine.Pin(np_pin)   # Set GPIO to output to drive NeoPixels
np = neopixel.NeoPixel(pin, 24)   # Create NeoPixel driver on GPIO0 for 24 pixels

# Network setup
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Try connecting to WiFi and syncing time, until success
while True:
    time.sleep(.25)
    np.fill((randint(0,10), randint(0,10), randint(0,10)))
    np.write()
    print('.')
    try:
        if not sta.isconnected():
            sta.connect(wifi_SSID[wifi_id], wifi_PWD[wifi_id])
            while not sta.isconnected():
                pass
                print('TE')
                np.fill((randint(0,10), randint(0,10), randint(0,10)))
                np.write()
                time.sleep(.2)
                
        print('WIFI Connection successful')
    
        try:
            ntptime.settime()  # Sync time from NTP server
            print("Time synchronized successfully")
            break
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
    
    #pixel_range = ck_type# == 12 else 24
    return get_pix_value(hour, ip=24)#, ct=pixel_range))

def f_to_i(a, b, c):
    return int(a), int(b), int(c)

def update_color(r, g, b, i, dim=False):
    #if ck_type == 12 and actual_time[3] >= 12:
    #    r, g, b = f_to_i(r/2, g/2, b/2)  # Dim colors by 50% for PM#'''# work in progress
    

    tup = np[i]
    nr = r if r != '-' else tup[0]
    ng = g if g != '-' else tup[1]
    nb = b if b != '-' else tup[2]
    if dim:
        nr = round(nr/8)
        ng = round(ng/8)
        nb = round(nb/8)
        #print(nr)
        #print(ng)
        #print(nb)

    
    write(nr, ng, nb, i)
    
def make_markings_clear():
    update_color('-','-','-', orient(0), dim=True)
    update_color('-','-','-', orient(6), dim=True)
    update_color('-','-','-', orient(12), dim=True)
    update_color('-','-','-', orient(18), dim=True)
    update_color('-','-','-', orient(0), dim=True)
    '''update_color(0,0,0, orient(0), dim=True)
    update_color(0,0,0, orient(6), dim=True)
    update_color(0,0,0, orient(12), dim=True)
    update_color(0,0,0, orient(18), dim=True)'''


# Main loop
while True:
    actual_time = time.localtime(time.time() + UTC_OFFSET)
    print(actual_time)
    
    np.fill(bg_col)  # Fill background color
    make_markings_clear()
    
    # Update NeoPixels for second, minute, and hour
    update_color(254, '-', '-', get_sec())   # Red for seconds
    update_color('-', 70, '-', get_min())   # Green for minutes
    update_color('-', '-', 250, get_hr())    # Blue for hours
    make_markings_clear()
    
    np.write()  # Refresh the LEDs
    time.sleep(0.5)


