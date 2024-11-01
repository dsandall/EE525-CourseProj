import pandas as pd
import numpy as np
import glob

# Function to load and process CSV files
def load_and_average_csvs(file_paths, resample_rate):
    all_data = []

    # Step 1: Read all CSV files
    for file in file_paths:
        df = pd.read_csv(file, header=None, names=['Time', 'a', 'b', 'AccelZ1', 'd', 'f', 'AccelZ2'])
        df.drop(['a', 'b', 'd', 'f'], axis=1, inplace=True)

        df['AccelZ1'] = pd.to_numeric(df['AccelZ1'], errors='coerce') 
        df['AccelZ2'] = pd.to_numeric(df['AccelZ2'], errors='coerce') 
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        
        # Convert Time to timedelta format (assuming Time is in seconds)
        df['Time'] = pd.to_timedelta(df['Time'], unit='s')
        all_data.append(df)

    # Step 2: Combine DataFrames
    combined_df = pd.concat(all_data, ignore_index=True)

    # Step 3: Set 'Time' as index
    combined_df.set_index('Time', inplace=True)
    combined_df.dropna(inplace=True)

    # Resample and interpolate
    resampled_df = combined_df.resample(resample_rate).mean()
    interpolated_df = resampled_df.interpolate(method='time')

    # Reset index to move Time back to a column
    averaged_df = interpolated_df.reset_index()

    # Convert Time from timedelta to float in seconds
    averaged_df['Time'] = averaged_df['Time'].dt.total_seconds()

    # Add columns for AccelX1, AccelY1, AccelX2, AccelY2 (set to 0 as per your example)
    averaged_df['AccelX1'] = 0
    averaged_df['AccelY1'] = 0
    averaged_df['AccelX2'] = 0  # Initialize AccelX2
    averaged_df['AccelY2'] = 0  # Initialize AccelY2

    # Rearranging columns to match desired output
    averaged_df = averaged_df[['Time', 'AccelX1', 'AccelY1', 'AccelZ1', 'AccelX2', 'AccelY2', 'AccelZ2']]

    averaged_df.dropna(inplace=True)

    return averaged_df

# Example usage
file_paths = glob.glob("./averaging_data/*.csv")  # Adjust the path
resample_rate = '0.0016s'

averaged_data = load_and_average_csvs(file_paths, resample_rate)

# Save the averaged data to a new CSV file with headers
averaged_data.to_csv('averaged_data.csv', index=False, header=True)
