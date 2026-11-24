
import pandas as pd
from pathlib import Path

# Project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw dataset location
DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "atmosync_weather_raw.csv"
)

print("=" * 45)
print(" ATMOSYNC - DATA QUALITY VALIDATION")
print("=" * 45)

# Check dataset availability
if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

# Load raw dataset
df = pd.read_csv(DATA_FILE)

# 1. Dataset overview
print("\n1. DATASET OVERVIEW")
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Columns:", df.columns.tolist())

# 2. Missing values
print("\n2. MISSING VALUE CHECK")
print(df.isnull().sum())

# 3. Duplicate records
print("\n3. DUPLICATE RECORD CHECK")
print("Duplicate rows:", df.duplicated().sum())

# 4. Location-wise record count
print("\n4. LOCATION-WISE RECORD COUNT")
print(df.groupby("location").size())

print("\n" + "=" * 45)
print(" VALIDATION COMPLETED")
print("=" * 45)
