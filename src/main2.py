#!/usr/bin/env python
"""Released under the MIT License
Copyright 2015, 2016 MrTijn/Tijndagamer
"""

import os
import csv
from mpu6050 import mpu6050
import time
from datetime import datetime

sensor = mpu6050(0x68)
sensor.set_accel_range(mpu6050.ACCEL_RANGE_2G)
sensor.set_filter_range()
print("Accelerometer Alive")

print("homing printer")
os.system("echo G28 > ~/printer_data/comms/klippy.serial") # home printer
time.sleep(30)

# Generate a unique filename with the current date and time
start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f'sensor_data_{start_time}.csv'

# Open a CSV file to store the data
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header for the CSV file
    writer.writerow(["Time (s)", "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Temperature (C)"])
    
    # Start timing with a high-resolution timer
    start_timestamp = time.perf_counter()
    desired_interval = 0.001  # 1000 Hz (1 milliseconds)
    next_capture_time = start_timestamp + desired_interval

    os.system("echo G91  > ~/printer_data/comms/klippy.serial") # send printer +100mm along the x axis
    os.system("echo G1 X+100 F6000 > ~/printer_data/comms/klippy.serial") # send printer +100mm along the x axis
    os.system("echo G90  > ~/printer_data/comms/klippy.serial") # send printer +100mm along the x axis

    while True:
        # Get the current time
        current_time = time.perf_counter()

        if current_time >= next_capture_time:
            # Get sensor data
            accel_data = sensor.get_accel_data()
            gyro_data = {'x': 0, 'y': 0, 'z': 0} #sensor.get_gyro_data()
            temp = 0 #sensor.get_temp()

            # Calculate elapsed time from the start
            elapsed_time = current_time - start_timestamp

            # Write data to CSV
            writer.writerow([elapsed_time, accel_data['x'], accel_data['y'], accel_data['z'], 
                             gyro_data['x'], gyro_data['y'], gyro_data['z'], temp])

            # Print data to the console (optional)
            print(f"Time: {elapsed_time:.4f} s")
            print(f"Accel: x={accel_data['x']}, y={accel_data['y']}, z={accel_data['z']}")
            print(f"Gyro:  x={gyro_data['x']}, y={gyro_data['y']}, z={gyro_data['z']}")
            print(f"Temp:  {temp} C\n")

            # Schedule the next capture
            next_capture_time += desired_interval

        # time.sleep for a very short time to prevent high CPU usage
        time.sleep(0.0001)
