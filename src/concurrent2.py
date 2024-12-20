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

END_TIME = 30.0
INITIAL_WAIT = 0.5

# Initialize ADXL345 and MPU6050
def initialize_sensors():
    mainADXL345.write_register(mainADXL345.REG_POWER_CTL, 0x08)  # Measure mode
    mainADXL345.write_register(mainADXL345.REG_BW_RATE, 0x0F)  # Max internal sample rate 
    mainADXL345.write_register(mainADXL345.REG_DATA_FORMAT, 0x00)  # +/- 2g, 10bit mode
    print("ADXL345 Initialized")

    mpu = mpu6050(0x68)
    mpu.set_accel_range(mpu6050.ACCEL_RANGE_2G)
    mpu.set_filter_range(filter_range=mpu6050.FILTER_BW_256)
    print("MPU6050 Initialized")
    return mpu

def collect_data(mpu, duration, initial_wait):
    """
    Collects accelerometer data from MPU6050 and ADXL345 for a given duration
    and initial wait time.
    
    Args:
        mpu (MPU6050): The MPU6050 sensor object.
        duration (float): Total duration to collect data in seconds.
        initial_wait (float): Duration to wait before starting data collection.
    
    Returns:
        list: Collected data records.
    """

    sent_cmd = False
    data_records = []
    start_timestamp = time.perf_counter()

    # Collect data for the specified duration
    end_capture_time = start_timestamp + duration
    while time.perf_counter() < end_capture_time:
        current_time = time.perf_counter()
        
        # Get data
        mpu_data = mpu.get_accel_Z()
        adxl_data = mainADXL345.read_accelerometer_z()
        adxl_data = max(-20, min(20, adxl_data))
        
        # Calculate elapsed time from the start
        elapsed_time = current_time - start_timestamp
        if elapsed_time > initial_wait and not sent_cmd:
            # Send G-code command after the initial wait
            print("Sending G-code command...")
            # os.system("echo G91 > ~/printer_data/comms/klippy.serial")  # Relative positioning mode
            # os.system("echo G1 X-100 F6000 > ~/printer_data/comms/klippy.serial")  # Move -100mm along the X-axis
            ## os.system("echo G90 > ~/printer_data/comms/klippy.serial")  # Absolute positioning mode
            sent_cmd = True

        # Store data in the records list
        data_records.append([elapsed_time, 0, 0, mpu_data, 0, 0, adxl_data])

    return data_records

def write_data_to_csv(filename, data_records):
    """Writes collected data records to a CSV file."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header for the CSV file
        writer.writerow(["Time", "AccelX1", "AccelY1", "AccelZ1",
                         "AccelX2", "AccelY2", "AccelZ2"])
        
        # Write all records at once
        writer.writerows(data_records)

def main():
    # Initialize sensors
    mpu = initialize_sensors()
    
    # Home the printer
    print("Homing printer")
    os.system("echo G28 > ~/printer_data/comms/klippy.serial")  # Home printer
    time.sleep(25)

    # Generate a unique filename with the current date and time
    start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'sensors_data_{start_time}_stationary_30s.csv'

    # Start data collection
    print("Starting data collection...")
    
    # Wait, then collect data
    data_records = collect_data(mpu, END_TIME + INITIAL_WAIT, INITIAL_WAIT)
    
    # Data capture is complete
    print("Data capture complete.")
    mainADXL345.spi.close()
    
    # Write data to CSV after collection
    write_data_to_csv(filename, data_records)

if __name__ == "__main__":
    main()
