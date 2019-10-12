# import Relevant Librares
import wiringpi
import time

# Variables
last_interrupt_time = 0
buffer = bytes("")

humidity = 0.0
temp = 0
light = 0
dac_out = 0.0

# function declarations

def gpio_cleanup():
    wiringpi.pwmWrite(1, 0) # Effectively turn off pwm
    wiringpi.digitalWrite(8, 0) # Turn off pin 8


def init_pi():
    # init pins and wiring pi
    wiringpi.wiringPiSetup()
    wiringpi.wiringPiSPISetup(0, 244141)

    # init pwm
    wiringpi.pinMode(1,wiringpi.PWM_OUTPUT) # initialise pin 1 as PWM
    wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
    wiringpi.pwmSetClock(3840)
    wiringpi.pwmSetRange(2500) # Give us about 1/2 s delay
    wiringpi.pwmWrite(1, 0) # Start pwm with no output

    # init buttons
    # set up stop/start button
    wiringpi.pinMode(0, wiringpi.INPUT)
    wiringpi.pullUpDnControl(0, wiringpi.PUD_UP)

    # set up frequency switch button
    wiringpi.pinMode(2, wiringpi.INPUT)
    wiringpi.pullUpDnControl(2, wiringpi.PUD_UP)

    # set up reset button
    wiringpi.pinMode(3, wiringpi.INPUT)
    wiringpi.pullUpDnControl(3, wiringpi.PUD_UP)

    # init interrupts
    wiringpi.wiringPiISR(0, wiringpi.INT_EDGE_FALLING, monitoring) # stop/start
    wiringpi.wiringPiISR(2, wiringpi.INT_EDGE_FALLING, switch_frequency) # frequency switch
    wiringpi.wiringPiISR(3, wiringpi.INT_EDGE_FALLING, reset) # reset switch

# callback functions
def monitoring():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time

    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Monitoring")

        # INTERRUPT CODE END
        last_interrupt_time = int(round(time.time() * 1000)) # resetting interrupt time

def switch_frequency():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time

    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Switching Frequency")

        # INTERRUPT CODE END
        last_interrupt_time = int(round(time.time() * 1000)) # resetting interrupt time

def reset():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time

    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Resetting")

        # INTERRUPT CODE END
        last_interrupt_time = int(round(time.time() * 1000)) # resetting interrupt time

# Monitoring code
def start_monitoring():
    time.sleep(1)

def stop_monitoring():
    time.sleep(1)

# LED Control
def start_LED():
    wiringpi.pwmWrite(1, 512) # Start pwm with no output

def stop_LED():
    wiringpi.pwmWrite(1, 0) # Start pwm with no output

def display_headings():
    print("-------------------------------------------------------------------")
    print("| RTC Time | Sys Time | Humidity | Temp | Light | DAC out | Alarm |")
    print("-------------------------------------------------------------------")

def output_data():
    print("| {:^8} |".format(str(temp)) + "Sys Time | Humidity | Temp | Light | DAC out | Alarm |")
    print("-------------------------------------------------------------------")

def read_ADC():
    time.sleep(1)

"""
def set_RTC():
    

def get_RTC():
    

def get_DAC():
"""

# MAIN FUNCTION = ENTRY POINT
def main():
    init_pi()
    #output_data()
    while True:
        # Add stuff
	    continue



# Only run the functions if 
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off your GPIOs here
        gpio_cleanup()
    except Exception as e:
        print("An unusual error occured:")
        print(e)
        # Turn off GPIOs
        gpio_cleanup()
