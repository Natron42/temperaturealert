Execute with sg dialout -c 'python3 main.py'


explore my usb temperaturealert dongle and try fix my python program main.py to connect to it
[197511.866733] ftdi_sio 3-7.4.1:1.0: FTDI USB Serial Device converter detected
[197511.866763] usb 3-7.4.1: Detected FT232R
[197511.867270] usb 3-7.4.1: FTDI USB Serial Device converter now attached to ttyUSB0

The device is very old and the company no longer exists.  The dongle reads the temperature.
The dongle may need to activate for read with a command word.  R\r command

write the date time with zero and 24 hoour time filled so it lines up as yyyymmdd:hh:mm
current temperature in °F

Have it write to the log every 15 minutes and start at the top of the hour.


Version 2
write to Google Doc https://docs.google.com/document/d/1pakJ4mGTCINLysE-wrXpV50rKjhVCIImlh9_giLEzCs/edit?usp=sharing

