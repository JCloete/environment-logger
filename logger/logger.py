# import Relevant Librares
#import RPi.GPIO as GPIO
import time

humidity = 0.0
temp = 0
light = 0
dac_out = 0.0

def init_pi():
    

def display_headings():
    print("-------------------------------------------------------------------")
    print("| RTC Time | Sys Time | Humidity | Temp | Light | DAC out | Alarm |")
    print("-------------------------------------------------------------------")

def output_data():
    print("| {:^8} |".format(str(temp)) + "Sys Time | Humidity | Temp | Light | DAC out | Alarm |")
    print("-------------------------------------------------------------------")

"""
def start_monitoring():


def stop_monitoring():


def switch_frequency():


def reset():


def set_RTC():
    

def get_RTC():
    

def get_temp():
    

def get_humidity():
    

def get_light():
    

def start_LED():
    

def stop_LED():
    

def get_DAC():
"""

def main():
    display_headings()
    time.sleep(1)
    output_data()
    time.sleep(1)



# Only run the functions if 
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off your GPIOs here
        #GPIO.cleanup()
    except Exception as e:
        print("An unusual error occured:")
        print(e)
        # Turn off GPIOs
        #GPIO.cleanup()