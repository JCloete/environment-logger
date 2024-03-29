# import Relevant Librares
import datetime
import wiringpi
import math
import os
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import spidev
import smbus
import BlynkLib

# Variables
last_interrupt_time = 0
last_alarm_time = 0

#BLYNK_AUTH = "QEQW3pahNPNIQ0KNypUZZCJIaRw2KoAl"
BLYNK_AUTH = "i8D2wMYEaIWhZ08jz7nq8ESe1X7UFQCi"
blynk = BlynkLib.Blynk(BLYNK_AUTH)

frequency = 1
alarm = 0
monitor = 1
humidity =0
temp = 0
light = 0
dac_out = 0.0
data1s = 0
data2s = 0
sys_secs = 0

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

    # set up alarm dismiss button
    wiringpi.pinMode(4, wiringpi.INPUT)
    wiringpi.pullUpDnControl(4, wiringpi.PUD_UP)

    # init interrupts
    wiringpi.wiringPiISR(0, wiringpi.INT_EDGE_FALLING, monitoring) # stop/start
    wiringpi.wiringPiISR(2, wiringpi.INT_EDGE_FALLING, switch_frequency) # frequency switch
    wiringpi.wiringPiISR(3, wiringpi.INT_EDGE_FALLING, reset) # reset switch
    wiringpi.wiringPiISR(4, wiringpi.INT_EDGE_FALLING, dismiss) #dismiss alarm

#@blynk.handle_event("read v1")
#def read_virtual_pin_handler(vpin):
#	temp = (read_ADC(2)*3.3/1024 - 0.5)/0.01
#	humidity = read_ADC(0)
#	light = read_ADC(1)
#	blynk.virtual_write(1, temp)
#	blynk.virtual_write(2, light)
#	blynk.virtual_write(3, humidity)

# callback functions
def monitoring():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time

    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Monitoring")
	global monitor
	if(monitor):
		monitor = 0
	else:
		monitor = 1

        # INTERRUPT CODE END
        last_interrupt_time = int(round(time.time() * 1000)) # resetting interrupt time

def dismiss():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time
    global alarm
    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Dismissing alarm")
	alarm = 0
        # INTERRUPT CODE END
        last_interrupt_time = int(round(time.time() * 1000)) # resetting interrupt time

def switch_frequency():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time

    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Switching Frequency")
	global frequency
	if(frequency==1):
		frequency=2
	elif(frequency==2):
		frequency=5
	elif(frequency==5):
		frequency=1

        # INTERRUPT CODE END
        last_interrupt_time = int(round(time.time() * 1000)) # resetting interrupt time

def reset():
    # Set up debouncing
    interrupt_time = int(round(time.time() * 1000)) # setting current interrupt time
    global last_interrupt_time
    global sys_secs

    if (interrupt_time - last_interrupt_time > 300):
        # INTERRUPT CODE BEGIN
        print("Resetting")
	sys_secs = 0
	os.system('printf "\033c"')
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
    print ('-------------------------------------------------------------------')
    print ("| RTC Time | Sys Time | Humidity | Temp | Light | DAC out | Alarm |")
    print ('-------------------------------------------------------------------')

def output_data():
    global dac_out
    global alarm
    global last_alarm_time
    global sys_secs
    global blynk
    global BLYNK_AUTH
    blynk=BlynkLib.Blynk(BLYNK_AUTH)

    humidity = read_ADC(0)*3.3/1024
    temp = (read_ADC(2)*3.3/1024-0.5)/0.01-3
    light = read_ADC(1)
    dac_out = (light/1023.0)*humidity
    sys_time = keep_sys_time()

    if((dac_out> 2.65 or dac_out< 0.65) and (monitor)):
	alarm_time = sys_secs
	if(alarm_time-last_alarm_time>180 or last_alarm_time==0 or alarm == 1):
		if(alarm==0):
			alarm = 1
			last_alarm_time = alarm_time
        else:
		alarm = 0
    else:
	alarm = 0

    if(alarm):
	wiringpi.pwmWrite(1,500)
	alarm_string = "*"
    else:
	wiringpi.pwmWrite(1,0)
	alarm_string = " "

    if(monitor):
    	longun = ("| {:^8} |".format(str(rtc_val())) + " {:^8} |".format(sys_time)+" {0:6.2f} V |".format(humidity)
		+" {0:2.0f} C |".format(temp)+" {0:5.0f} |".format(light)
		+"  {0:3.2f} V |".format(dac_out)+" {:^5} |".format(alarm_string))
	print(longun)
    	print("-------------------------------------------------------------------")
    	blynk.virtual_write(0, longun+"\n")
	blynk.virtual_write(0, "-------------------------------------------------------------------\n")
    	blynk.virtual_write(1, temp)
    	blynk.virtual_write(2, light)
    	blynk.virtual_write(3, humidity)
	blynk.virtual_write(5, dac_out)
    write_DAC(int(dac_out*(1023/3.3)))
    time.sleep(frequency)

def keep_sys_time():
	global sys_secs
	sys_mins = int(math.floor(sys_secs/60))
	secs = sys_secs%60
	sys_hours = int(math.floor((sys_mins)/60))
	mins = sys_mins%60
	stringy = "{:02d}:{:02d}:{:02d}".format(sys_hours, mins, secs)
	sys_secs+= frequency
	return(stringy)

def init_ADC():
	global mcp
        mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))

def read_ADC(channel):
        value = mcp.read_adc(channel)
        return value

def write_DAC(val):
	b1 = 0b0011 << 4 | val >> 6
	b2 = (val << 2)%256

	spi = spidev.SpiDev()
	spi.open(0,1)
	spi.max_speed_hz = 1000000
	spi.mode = 0
	send_data = [b1, b2]
	spi.xfer(send_data)

def conv(val):
	return (((val)&0x0f)+((val) >> 4)*10)

def rtc_val():
	#bus = smbus.SMBus(1)
	#hours = conv(bus.read_byte_data(0x6f,0x02)&0x3f)
	#mins = conv(bus.read_byte_data(0x6f,0x01)&0x7f)
	#secs = conv(bus.read_byte_data(0x6f, 0x00)&0x7f)
	#stringy = "{:02}:{:02}:{:02}".format(hours,mins,secs)
	#return(stringy)
	return(time.strftime("%H:%M:%S", time.localtime()))

# MAIN FUNCTION = ENTRY POINT
def main():
    init_pi()
    #output_data()
    init_ADC()
    display_headings()
    while True:
	blynk.run()
	output_data()

# Only run the functions if
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
	#frequency = 1
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
