import pandas as pd
# import os
import numpy as np


def get_NUFORC_archive():
    data_path = 'NUFORC archive/complete.csv'
    data = pd.read_csv(data_path, on_bad_lines='skip')
    # Convert 'datetime' to datetime object
    data['datetime'] = pd.to_datetime(data['datetime'], errors='coerce')
    data['datetime_str'] = data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Convert to string
    # Convert 'duration (seconds)' to numeric (float)
    data['duration (seconds)'] = pd.to_numeric(data['duration (seconds)'], errors='coerce')

    # Fill missing values or drop them based on your preference
    # For example, fill missing countries with 'unknown'
    data['country'].fillna('unknown', inplace=True)

    return data

def add_occurrences_based_on_range(df, lat_col='latitude', lon_col='longitude', grid_size=0.1):
    """
    Adds an 'occurrences' column to the DataFrame based on the frequency of sightings
    within a specified grid size for latitude and longitude variations.

    Parameters:
    - df: pandas DataFrame containing the UFO sightings data.
    - lat_col: Name of the column containing latitude values.
    - lon_col: Name of the column containing longitude values.
    - grid_size: The size of the grid to approximate geographical grouping (in degrees).

    Returns:
    - DataFrame with an additional 'occurrences' column.
    """
    # Round the latitude and longitude to group nearby sightings together
    df['rounded_lat'] = np.round(df[lat_col].astype(float) / grid_size) 
    df['rounded_lon'] = np.round(df[lon_col].astype(float) / grid_size)
    
    # Create a temporary key to group by based on the rounded values
    df['temp_key'] = df['rounded_lat'].astype(str) + '_' + df['rounded_lon'].astype(str)
    
    # Count the occurrences and add as a new column
    df['occurrences'] = df.groupby('temp_key')['temp_key'].transform('count')
    df['radius'] = np.log(df['occurrences']+1)* 1000  # Adjust scaling factor as needed
    # Drop the temporary columns
    df.drop(['temp_key', 'rounded_lat', 'rounded_lon'], axis=1, inplace=True)
    
    return df