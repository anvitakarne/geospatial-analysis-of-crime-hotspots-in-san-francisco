import pandas as pd
import numpy as np

# **1. Load Datasets**
police_incidents_path = "data/Police_Department_Incident_Reports.csv"  # Update with correct path
facilities_path = "data/City_Facilities.csv"  # Update with correct path

police_incidents = pd.read_csv(police_incidents_path)
facilities = pd.read_csv(facilities_path)

# Print basic info
print(f"📊 Police Incidents - Shape: {police_incidents.shape}, Columns: {list(police_incidents.columns)}")
print(f"📊 Facilities - Shape: {facilities.shape}, Columns: {list(facilities.columns)}")

# **2. Drop Unnecessary Columns**
columns_to_drop_incidents = ['CAD Number', 'Filed Online', 'Point', 'Row ID',
                             'Incident Number', 'Report Type Code', 'Report Type Description',
                             'Supervisor District', 'Supervisor District 2012', 'CNN']

columns_to_drop_facilities = ['block_lot', 'gross_sq_ft', 'city_tenants', 'land_id',
                              'geom', 'data_last_updated', 'data_as_of', 'data_loaded_at']

police_incidents_clean = police_incidents.drop(columns=columns_to_drop_incidents, errors="ignore")
facilities_clean = facilities.drop(columns=columns_to_drop_facilities, errors="ignore")

# **3. Handle Missing Values**
# Fill missing categorical values with 'Unknown'
categorical_columns_incidents = ['Incident Category', 'Incident Subcategory', 'Analysis Neighborhood', 'Intersection']
for col in categorical_columns_incidents:
    police_incidents_clean[col] = police_incidents_clean[col].fillna('Unknown')

# Drop rows with missing latitude & longitude
police_incidents_clean = police_incidents_clean.dropna(subset=['Latitude', 'Longitude'])

# Repeat for facilities dataset
categorical_columns_facilities = ['address', 'jurisdiction', 'supervisor_district']
for col in categorical_columns_facilities:
    facilities_clean[col] = facilities_clean[col].fillna('Unknown')

facilities_clean = facilities_clean.dropna(subset=['latitude', 'longitude'])

# **4. Save Cleaned Data**
police_incidents_clean.to_csv("processed_data/Police_Incidents_Clean.csv", index=False)
facilities_clean.to_csv("processed_data/City_Facilities_Clean.csv", index=False)

# **5. Print Summary**
print(f"Police Incidents - After Cleaning: {police_incidents_clean.shape}")
print(f"Facilities - After Cleaning: {facilities_clean.shape}")
print("Preprocessed data saved in 'processed_data/' folder.")
