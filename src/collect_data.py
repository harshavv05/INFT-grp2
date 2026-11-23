
# ==========================================
# ATMOSYNC - MICRO-CLIMATE ANALYTICS
# MEMBER 1: DATA COLLECTION
# ==========================================

import requests
import pandas as pd
from pathlib import Path

print("AtmoSync Data Collection Started!")

# Project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw dataset storage
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)

# Historical API
API_URL = "https://archive-api.open-meteo.com/v1/archive"

# Date range
START_DATE = "2025-10-01"
END_DATE = "2025-10-31"

TIMEZONE = "Asia/Kolkata"

# Bengaluru locations

LOCATIONS = {
    "Electronic City": {
        "latitude": 12.8452,
        "longitude": 77.6602
    },

    "Whitefield": {
        "latitude": 12.9698,
        "longitude": 77.7500
    },

    "Jayanagar": {
        "latitude": 12.9250,
        "longitude": 77.5838
    },

    "Hebbal": {
        "latitude": 13.0358,
        "longitude": 77.5970
    }
}

# Weather variables to collect

WEATHER_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "apparent_temperature",
    "cloud_cover",
    "pressure_msl"
]

# ==========================================
# FETCH WEATHER DATA FOR ONE LOCATION
# ==========================================

def fetch_location_weather(name, latitude, longitude):

    print(f"\nFetching weather data for {name}...")

    # API request parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(WEATHER_VARIABLES),
        "timezone": TIMEZONE,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "models": "era5_land"
    }

    # Send request to Open-Meteo
    response = requests.get(
        API_URL,
        params=params,
        timeout=60
    )

    # Check whether request succeeded
    response.raise_for_status()

    # Convert API response into Python dictionary
    result = response.json()

    if result.get("error"):
        raise RuntimeError(result.get("reason"))

    # Extract hourly weather information
    hourly_data = result["hourly"]

    # Convert information into a Pandas DataFrame
    location_df = pd.DataFrame(hourly_data)

    # Add location information
    location_df["location"] = name

    location_df["requested_latitude"] = latitude
    location_df["requested_longitude"] = longitude

    # Preserve actual API grid coordinates
    location_df["grid_latitude"] = result["latitude"]
    location_df["grid_longitude"] = result["longitude"]

    print(f"Collected {len(location_df)} records for {name}")

    return location_df

# ==========================================
# MAIN DATA COLLECTION PROGRAM
# ==========================================

def main():

    all_weather_data = []

    # Loop through all four locations
    for name, coordinates in LOCATIONS.items():

        latitude = coordinates["latitude"]
        longitude = coordinates["longitude"]

        location_df = fetch_location_weather(
            name,
            latitude,
            longitude
        )

        all_weather_data.append(location_df)

    # Combine all four location datasets
    final_df = pd.concat(
        all_weather_data,
        ignore_index=True
    )

    print("\nAll locations collected successfully!")

    print("Total records:", len(final_df))

    return final_df


# Execute the program
if __name__ == "__main__":
    weather_df = main()

# ==========================================
# SAVE RAW WEATHER DATASET
# ==========================================

output_file = RAW_FOLDER / "atmosync_weather_raw.csv"

weather_df.to_csv(
    output_file,
    index=False
)

print("\nRaw dataset saved successfully!")
print("File location:", output_file)
