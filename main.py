#version 4.2 fix outside temp location (use zip code 22932 instead of name)

import os
import requests
import serial
import struct
import sys
import time
from datetime import datetime, timedelta

if sys.platform.startswith('win'):
    PORT = 'COM3'
elif sys.platform == 'darwin':
    PORT = '/dev/tty.usbserial-0001'
else:
    PORT = '/dev/ttyUSB0'
BAUD = 9600
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temperaturealert.log')
APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbz-fTETpM-3AmclY_cJ2O3hC5OJE1q8XowPNXluFz-c184h4gK5OC03TeZcZodqNKfjkA/exec'
OUTSIDE_LOCATION = '22932'

# Packet format from device (18 bytes):
#   bytes 0-8:  zero-byte header (padding)
#   bytes 9-10: temperature (little-endian int16, DS18B20 units: raw/16 = °C)
PACKET_LEN = 18
TEMP1_OFFSET = 9


def read_temperature_f(ser):
    ser.reset_input_buffer()
    ser.write(b'R\r')
    time.sleep(1.0)
    data = ser.read(64)
    if len(data) < PACKET_LEN:
        return None
    raw = struct.unpack_from('<h', data, TEMP1_OFFSET)[0]
    celsius = raw / 16.0
    return celsius * 9 / 5 + 32


def seconds_to_next_quarter():
    """Seconds until the next :00/:15/:30/:45 boundary."""
    now = datetime.now()
    elapsed = (now.minute % 15) * 60 + now.second + now.microsecond / 1e6
    return 15 * 60 - elapsed


def get_outside_temp_f():
    try:
        r = requests.get(f'https://wttr.in/{OUTSIDE_LOCATION}?format=j1', timeout=10)
        return float(r.json()['current_condition'][0]['temp_F'])
    except Exception as e:
        print(f"Weather fetch failed: {e}")
        return None


def log_temperature(ser):
    if ser is None:
        temp_f = None
    else:
        try:
            temp_f = read_temperature_f(ser)
        except serial.SerialException as e:
            temp_f = None
            print(f"Serial error: {e}")

    outside_f = get_outside_temp_f()

    timestamp = datetime.now().strftime('%Y%m%d:%H:%M')
    indoor = f"{temp_f:.1f}°F" if temp_f is not None else "XX.X°F"
    outdoor = f" outside:{outside_f:.1f}°F" if outside_f is not None else "XX.X°F"
    line = f"{timestamp} {indoor}{outdoor}"

    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

    try:
        r = requests.post(APPS_SCRIPT_URL, data=line.encode('utf-8'), headers={'Content-Type': 'text/plain; charset=utf-8'}, timeout=10)
        print(f"Google Doc post: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"Google Doc post failed: {e}")


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        print(f"Connected to {PORT} at {BAUD} baud")
    except serial.SerialException as e:
        print(f"Warning: could not open {PORT}: {e}")
        print("Continuing without indoor sensor (indoor will log as XX.X°F)")
        ser = None

    print(f"Logging to {LOG_FILE}")

    try:
        # Record temperature immediately on startup
        log_temperature(ser)

        while True:
            wait = seconds_to_next_quarter()
            next_time = datetime.now() + timedelta(seconds=wait)
            print(f"Next log at {next_time.strftime('%Y%m%d:%H:%M')} (in {wait:.0f}s)")
            time.sleep(wait)
            log_temperature(ser)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if ser is not None:
            ser.close()


if __name__ == '__main__':
    main()
