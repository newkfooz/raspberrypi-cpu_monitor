# CPU and GPU temperature on display LCD 16x2:

# import
import RPi.GPIO as GPIO
import time
import subprocess
import psutil

# Define GPIO to LCD mapping
LCD_RS = 26
LCD_E  = 19
LCD_D4 = 13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 11
LED_ON = 15

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80   # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0   # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Degree character
bytes0 = [12, 18, 18, 12, 0, 0, 0, 0]
bytes1 = [0, 0, 0, 0, 0, 0, 31, 0]
bytes2 = [0, 0, 0, 0, 31, 0, 31, 0]
bytes3 = [0, 0, 31, 0, 31, 0, 31, 0]
bytes4 = [31, 0, 31, 0, 31, 0, 31, 0]
bytesn = [0, 0, 0, 0, 0, 0, 0, 0]

def main():
  # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LED_ON, GPIO.OUT) #Backlight enable

  # Initialise display
  lcd_init()

  cgchar(0x40, bytes0) # Set up a custom degree character as char 0
  cgchar(0x48, bytes1) # Set up a custom degree character as char 1
  cgchar(0x50, bytes2) # Set up a custom degree character as char 2
  cgchar(0x58, bytes3) # Set up a custom degree character as char 3
  cgchar(0x60, bytes4) # Set up a custom degree character as char 4
  cgchar(0x68, bytesn) # Set up a custom degree character as char 5

  lcd_backlight(False)
  time.sleep(0.2)
  lcd_backlight(True)
  time.sleep(0.2)
  lcd_backlight(False)
  time.sleep(0.1)
  lcd_backlight(True)
  time.sleep(0.1)
  lcd_backlight(False)
  time.sleep(0.3)
  lcd_backlight(True)
  time.sleep(0.1)
  lcd_backlight(False)
  time.sleep(0.3)
  lcd_backlight(True)
  time.sleep(0.2)
  lcd_backlight(False)
  time.sleep(0.3)
  lcd_backlight(True)
  time.sleep(0.1)
  lcd_backlight(False)
  time.sleep(0.1)
  lcd_backlight(True)
  time.sleep(0.2)
  lcd_backlight(False)
  time.sleep(0.3)
  lcd_backlight(True)
  time.sleep(0.5)

  while True:

    cpu_tempC = get_cpu_tempC()
    gpu_tempC = get_gpu_tempC()

    cpuT = "CPU: %.1f" % cpu_tempC
    gpuT = "GPU: %.1f" % gpu_tempC

    # The coordinates number is an exadecimal value  0123456789ABCDEF
    lcd_string(cpuT + " C", LCD_LINE_1)
    lcd_byte(0x89, LCD_CMD)
    lcd_byte(0, LCD_CHR)
    lcd_string(gpuT + " C", LCD_LINE_2)
    lcd_byte(0xC9, LCD_CMD)
    lcd_byte(0, LCD_CHR)

    cpu0_perc = get_corePerc(0)
    cpu1_perc = get_corePerc(1)
    cpu2_perc = get_corePerc(2)
    cpu3_perc = get_corePerc(3)

    d0 = int(diagram(cpu0_perc))
    if d0 < 5:
      lcd_byte(0x8C, LCD_CMD)
      lcd_byte(5, LCD_CHR)
      lcd_byte(0xCC, LCD_CMD)
      lcd_byte(d0, LCD_CHR)
    else:
      lcd_byte(0x8C, LCD_CMD)
      uppd0 = d0 - 4
      lcd_byte(uppd0, LCD_CHR)
      lcd_byte(0xCC, LCD_CMD)
      lcd_byte(4, LCD_CHR)

    d1 = int(diagram(cpu1_perc))
    if d1 < 5:
      lcd_byte(0x8D, LCD_CMD)
      lcd_byte(5, LCD_CHR)
      lcd_byte(0xCD, LCD_CMD)
      lcd_byte(d1, LCD_CHR)
    else:
      lcd_byte(0x8D, LCD_CMD)
      uppd1 = d1 - 4
      lcd_byte(uppd1, LCD_CHR)
      lcd_byte(0xCD, LCD_CMD)
      lcd_byte(4, LCD_CHR)

    d2 = int(diagram(cpu2_perc))
    if d2 < 5:
      lcd_byte(0x8E, LCD_CMD)
      lcd_byte(5, LCD_CHR)
      lcd_byte(0xCE, LCD_CMD)
      lcd_byte(d2, LCD_CHR)
    else:
      lcd_byte(0x8E, LCD_CMD)
      uppd2 = d2 - 4
      lcd_byte(uppd2, LCD_CHR)
      lcd_byte(0xCE, LCD_CMD)
      lcd_byte(4, LCD_CHR)

    d3 = int(diagram(cpu3_perc))
    if d3 < 5:
      lcd_byte(0x8F, LCD_CMD)
      lcd_byte(5, LCD_CHR)
      lcd_byte(0xCF, LCD_CMD)
      lcd_byte(d3, LCD_CHR)
    else:
      lcd_byte(0x8F, LCD_CMD)
      uppd3 = d3 - 4
      lcd_byte(uppd3, LCD_CHR)
      lcd_byte(0xCF, LCD_CMD)
      lcd_byte(4, LCD_CHR)

###### Symbols Control #############
#    lcd_byte(0xC0, LCD_CMD)
#    lcd_byte(5, LCD_CHR)
#    lcd_byte(1, LCD_CHR)
#    lcd_byte(2, LCD_CHR)
#    lcd_byte(3, LCD_CHR)
#    lcd_byte(4, LCD_CHR)

###### Prints the percentage of each CPU core

#    lcd_string(per0 + "%", 0x80)
#    lcd_string(per1 + "%", 0x8A)
#    lcd_string(per2 + "%", 0xC0)
#    lcd_string(per3 + "%", 0xCA)

    time.sleep(1)

###########################################################################################

def cgchar(CGCHR, byt):
  lcd_byte(CGCHR, LCD_CMD)
  for value in (byt[0],byt[1],byt[2],byt[3],byt[4],byt[5],byt[6],byt[7]):
    lcd_byte(value, LCD_CHR)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def get_cpu_tempC():
  # Read from file the CPU temperature
  tempFile = open("/sys/class/thermal/thermal_zone0/temp")
  cpu_temp = tempFile.read()
  tempFile.close()
  return float(cpu_temp)/1000

def get_gpu_tempC():
  # Read the output GPU temp from vcgencmd, decode it from byte to string,
  # cut the unnecessary text, obtaining a clean float
  x = subprocess.check_output(["vcgencmd", "measure_temp"])
  gpu_temp = x.decode("utf_8").replace( 'temp=', '' ).replace( '\'C', '' )
  return float(gpu_temp)

def get_corePerc(ncore):
  # this function provides the cpu core utilization as a percentage
  # if interval is > 0 compares system cpu times elapsed before and after the inteval (blocking)
  # if interval is 0.0 or None compares system cpu times elapsed since last call or module import, returning immediatly
  # percpu = True returns a list of floats representing the utilization as a percentage for each core
  list = psutil.cpu_percent(interval = None, percpu = True)
  perc_core = list[ncore]
  return float(perc_core)


def is_float(value):
  try:
    float(value)
    return True
  except:
    return False

def lcd_backlight(flag):
  # Toggle backlight on-off
  GPIO.output(LED_ON, flag)

def diagram(per):
  # Creates a pattern for the CPU cores, it is to put in the right place
  if float(per) < 12.5 and float(per) >= 0:
    return 1
  elif float(per) < 25:
    return 2
  elif float(per) < 37.5:
    return 3
  elif float(per) < 50:
    return 4
  elif float(per) < 62.5:
    return 5
  elif float(per) < 75:
    return 6
  elif float(per) < 87.5:
    return 7
  elif float(per) < 100:
    return 8
  elif float(per) >=100:
    return 8


def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__  == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
