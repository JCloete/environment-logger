# import Relevant Librares
import wiringpi
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import spidev
import smbus
import blynklib

# Variables
last_interrupt_time = 0

BLYNK_AUTH = 'eyK2PkL48piQSSER7hUeRdlPyMrJs_wj'
blynk = blynklib.Blynk(BLYNK_AUTH)

humidity = 0.0
temp = 0
light = 0
dac_out = 0.0
data1s = 0
data2s = 0

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

@blynk.handle_event("read v1")
def read_virtual_pin_handler(vpin):
	temp = (read_ADC(2)*3.3/1024 - 0.5)/0.01
	humidity = read_ADC(0)
	light = read_ADC(1)
	blynk.virtual_write(1, temp)
	blynk.virtual_write(2, light)
	blynk.virtual_write(3, humidity)

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
    print ('-------------------------------------------------------------------')
    print ("| RTC Time | Sys Time | Humidity | Temp | Light | DAC out | Alarm |")
    print ('-------------------------------------------------------------------')

def output_data():
    print("| {:^8} |".format(str(rtc_val())) + " {:^8} |".format(str(rtc_val()))+" {:^8} |".format(str(read_ADC(0)))
		+" {:^3}C |".format(str(read_ADC(2)))+" {:^5} |".format(str(read_ADC(1)))
		+" {:^6}V |".format("val")+" {:^5} |".format("*"))
    print("-------------------------------------------------------------------")

def init_ADC():
	global mcp
        mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))

def read_ADC(channel):
        value = mcp.read_adc(channel)
        return value

def write_DAC():
	val = 500
	b1 = 0b0011 << 4 | val >> 6
	b2 = (val << 2)%256

	spi = spidev.SpiDev()
	spi.open(0,1)
	spi.max_speed_hz = 1000000
	spi.mode = 0
	send = [b1, b2]
	spi.xfer(send)

def conv(val):
	return (((val)&0x0f)+((val) >> 4)*10)

def rtc_val():
	bus = smbus.SMBus(1)
	hours = conv(bus.read_byte_data(0x6f,0x02)&0x3f)
	mins = conv(bus.read_byte_data(0x6f,0x01)&0x7f)
	secs = conv(bus.read_byte_data(0x6f, 0x00)&0x7f)
	stringy = str(hours)+":"+str(mins)+":"+str(secs)
	return(stringy)

# MAIN FUNCTION = ENTRY POINT
def main():
    init_pi()
    #output_data()
    init_ADC()
    display_headings()
    while True:
	write_DAC()
	output_data()
        time.sleep(1)
	blynk.run()

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
