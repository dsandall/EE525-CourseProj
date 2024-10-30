#!/usr/bin/env python
"""Released under the MIT License
Copyright 2015, 2016 MrTijn/Tijndagamer
"""

import os
import csv
from mpu6050 import mpu6050
import mainADXL345
import time
from datetime import datetime

END_TIME = 4.0
INITIAL_WAIT = 0.5
# sample_t = 1 / 500
sample_t = 0

# Initialize ADXL345 and MPU6050
mainADXL345.write_register(mainADXL345.REG_POWER_CTL, 0x08)  # Measure mode
mainADXL345.write_register(mainADXL345.REG_DATA_FORMAT, 0x00)  # +/- 2g, full resolution
print("ADXL345 Initialized")

# mpu = mpu6050(0x68)
# mpu.set_accel_range(mpu6050.ACCEL_RANGE_2G)
# mpu.set_filter_range(filter_range=mpu6050.FILTER_BW_256)
# print("MPU6050 Initialized")


# mpu_data = mpu.get_accel_data()
adxl_data = mainADXL345.read_accelerometer()
# print(f"MPU: x={mpu_data['x']}, y={mpu_data['y']}, z={mpu_data['z']}")
print(f"ADXL345: x={adxl_data[0]}, y={adxl_data[1]}, z={adxl_data[2]}")

# Home the printer
print("Homing printer")
os.system("echo G28 > ~/printer_data/comms/klippy.serial")  # Home printer
time.sleep(25)

# Generate a unique filename with the current date and time
start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f'adxl_sensor_data_{start_time}.csv'

# Prepare a list to store the data
data_records = []

# Start timing with a high-resolution timer
start_timestamp = time.perf_counter()
next_capture_time = start_timestamp + sample_t

# Start data collection
print("Starting data collection...")

# Collect data for INITIAL_WAIT seconds
initial_wait_end_time = start_timestamp + INITIAL_WAIT

# Collect data for the initial wait period
while time.perf_counter() < initial_wait_end_time:
    current_time = time.perf_counter()

    # Get MPU data
    # mpu_data = mpu.get_accel_Z()
    mpu_data =0
    
    # Get ADXL data
    adxl_data = mainADXL345.read_accelerometer_z()
    # adxl_data = 0

    # Calculate elapsed time from the start
    elapsed_time = current_time - start_timestamp

    # Store data in the records list
    data_records.append([elapsed_time, 0, 0, mpu_data,
                            0,0,adxl_data])

    # Print data to the console (optional)
    # print(f"Time: {elapsed_time:.4f} s")
    # print(f"MPU: z={mpu_data}")
    # print(f"ADXL345: z={adxl_data}")
    
    # Schedule the next capture
    # next_capture_time += sample_t

# Send G-code command after the initial wait
print("Sending G-code command...")
os.system("echo G91 > ~/printer_data/comms/klippy.serial")  # Relative positioning mode
os.system("echo G1 X-100 F6000 > ~/printer_data/comms/klippy.serial")  # Move -100mm along the X-axis
# os.system("echo G90 > ~/printer_data/comms/klippy.serial")  # Absolute positioning mode

# Collect data for additional END_TIME seconds
end_capture_time = start_timestamp + END_TIME + INITIAL_WAIT
while time.perf_counter() < end_capture_time:
    current_time = time.perf_counter()

    # Get MPU data
    # mpu_data = mpu.get_accel_Z()
    mpu_data =0

    # Get ADXL data
    # adxl_data = mainADXL345.read_accelerometer_z()
    adxl_data = 0

    # Calculate elapsed time from the start
    elapsed_time = current_time - start_timestamp

    # Store data in the records list
    data_records.append([elapsed_time, 0, 0, mpu_data,
                            0,0,adxl_data])

    # Print data to the console (optional)
    # print(f"Time: {elapsed_time:.4f} s")
    # print(f"MPU: z={mpu_data}")
    # print(f"ADXL345: z={adxl_data}")
    
    # Schedule the next capture
    # next_capture_time += sample_t

# Data capture is complete
print("Data capture complete.")
mainADXL345.spi.close()

# Write data to CSV after collection
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header for the CSV file
    writer.writerow(["Time (s)", "Accel X1", "Accel Y1", "Accel Z1",
                     "Accel X2", "Accel Y2", "Accel Z2"])
    
    # Write all records at once
    writer.writerows(data_records)
