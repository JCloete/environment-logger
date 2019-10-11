# Python implementation of Blynk program
import blynklib
import random

BLYNK_AUTH = 'YourAuthToken'

# initialise blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

#initialise virtual pins
temp_pin = 1
light_pin = 2
humidity_pin = 3

#initialise variables, need to be updated with real values
temp = 23
light = 500
humidity = 20

READ_PRINT_MSG = "Temp: V{}, Light: V{}, Humidity: V{}"

# register handler for virtual pin reading
@blynk.handle_event('read V{}'.format(temp_pin))
def read_virtual_pin_handler(pin):
    print(READ_PRINT_MSG.format(temp_pin, light_pin, humidity_pin))
    blynk.virtual_write(temp_pin, temp)
    blynk.virtual_write(light_pin, light)
    blynk.virtual_write(humidity_pin, humidity)

###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()