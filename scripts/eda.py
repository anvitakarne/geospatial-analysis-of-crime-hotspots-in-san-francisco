import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial import cKDTree  # For nearest facility distance calculation
from geopy.distance import geodesic  # To measure geospatial distances

# Load cleaned dataset (update path if needed)
df = pd.read_csv("data/cs5834_police_incidents_clean.csv")
facilities_df = pd.read_csv("data/cs5834_facilities_clean.csv")

# Convert datetime column
df['Incident Datetime'] = pd.to_datetime(df['Incident Datetime'])
df['Year'] = df['Incident Datetime'].dt.year

# **1. Crime Trends Over the Years**
category_trends = df.groupby(['Year', 'Incident Subcategory']).size().reset_index(name='Count')

top_categories = (
    category_trends.groupby('Incident Subcategory')['Count']
    .sum().sort_values(ascending=False).head(10).index
)

category_trends_top = category_trends[category_trends['Incident Subcategory'].isin(top_categories)]

plt.figure(figsize=(14, 8))
for category in top_categories:
    data = category_trends_top[category_trends_top['Incident Subcategory'] == category]
    plt.plot(data['Year'], data['Count'], marker='o', label=category)

plt.title('Incident Subcategory Trends Over Years', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Number of Incidents', fontsize=14)
plt.legend(title='Incident Subcategory', fontsize=10)
plt.grid(alpha=0.3)
plt.savefig("figures/category_trends.png")  # Save figure
plt.show()

# **2. Crime Distribution by Neighborhood & Category**
neighborhood_category = df.groupby(['Analysis Neighborhood', 'Incident Category']).size().reset_index(name='Crime Count')

heatmap_data = neighborhood_category.pivot(index='Analysis Neighborhood', columns='Incident Category', values='Crime Count')

plt.figure(figsize=(15, 10))
sns.heatmap(heatmap_data, cmap='coolwarm', linewidths=0.5, annot=False)
plt.title('Crime Category Distribution by Neighborhood', fontsize=16)
plt.xlabel('Incident Category', fontsize=12)
plt.ylabel('Analysis Neighborhood', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.savefig("figures/neighborhood_heatmap.png")
plt.show()

# **3. High Crime Neighborhoods Without Facilities**
neighborhood_crime_count = df.groupby('Analysis Neighborhood').size().reset_index(name='Crime Count')
facilities_per_neighborhood = facilities_df.groupby('supervisor_district').size().reset_index(name='Facility Count')

neighborhood_analysis = neighborhood_crime_count.merge(
    facilities_per_neighborhood, left_on='Analysis Neighborhood',
    right_on='supervisor_district', how='left'
)
neighborhood_analysis['Facility Count'] = neighborhood_analysis['Facility Count'].fillna(0)

# Find underserved high-crime areas
high_crime_threshold = neighborhood_analysis['Crime Count'].quantile(0.75)
underserved_neighborhoods = neighborhood_analysis[
    (neighborhood_analysis['Crime Count'] > high_crime_threshold) & (neighborhood_analysis['Facility Count'] == 0)
]

plt.figure(figsize=(12, 6))
sns.barplot(data=underserved_neighborhoods.sort_values('Crime Count', ascending=False),
            x='Analysis Neighborhood', y='Crime Count', palette='Reds')

plt.title('Underserved Neighborhoods with High Crime and No Facilities', fontsize=16)
plt.xlabel('Neighborhood', fontsize=12)
plt.ylabel('Crime Count', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.savefig("figures/underserved_neighborhoods.png")
plt.show()

print("Underserved Neighborhoods with High Crime and No Facilities:")
print(underserved_neighborhoods[['Analysis Neighborhood', 'Crime Count', 'Facility Count']])

# **4. Nearest Facility Distance Analysis**
assert 'Latitude' in df.columns, "Latitude column missing"
assert 'Longitude' in df.columns, "Longitude column missing"
assert 'latitude' in facilities_df.columns, "Facility latitude column missing"
assert 'longitude' in facilities_df.columns, "Facility longitude column missing"

crime_coords = np.array(df[['Latitude', 'Longitude']])
facility_coords = np.array(facilities_df[['latitude', 'longitude']])

tree = cKDTree(facility_coords)
distances, indices = tree.query(crime_coords, k=1)

df['Nearest Facility'] = facilities_df.iloc[indices]['common_name'].values
df['Distance to Facility'] = distances

crime_by_facility = df.groupby('Nearest Facility')['Incident Category'].count().reset_index()
crime_by_facility.columns = ['Facility', 'Crime Count']

plt.figure(figsize=(12, 8))
top_facilities = crime_by_facility.sort_values(by='Crime Count', ascending=False).head(20)
sns.barplot(data=top_facilities, x='Crime Count', y='Facility', palette='viridis')
plt.title("Top 20 Facilities by Associated Crime Count")
plt.xlabel("Crime Count")
plt.ylabel("Facility")
plt.savefig("figures/crime_by_facility.png")
plt.show()

print(" EDA complete! Figures saved in the 'figures/' folder.")
