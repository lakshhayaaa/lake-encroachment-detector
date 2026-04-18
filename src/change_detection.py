import ee
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd

#Connect to Earth Engine and load median composites for 2019 and 2024
ee.Initialize(project="midyear-karma-484017-t7")
image_2019=ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterBounds(ee.Geometry.Point([76.9558, 11.0168])) \
    .filterDate("2019-01-01", "2019-12-31") \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10)) \
    .median()
image_2024=ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterBounds(ee.Geometry.Point([76.9558, 11.0168])) \
    .filterDate("2024-01-01", "2024-12-31") \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10)) \
    .median()
print("Median composites for 2019 and 2024 loaded successfully.")

# calculate NDBI for both years
def calculate_ndbi(image):
    nbdi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
    return nbdi

ndbi_2019 = calculate_ndbi(image_2019)
ndbi_2024 = calculate_ndbi(image_2024)
print("NDBI calculated for both years.")

# Calculate difference in NDBI between 2024 and 2019
ndbi_diff = ndbi_2024.subtract(ndbi_2019).rename('NDBI_Diff')
print("NDBI difference calculated between 2024 and 2019.")

#Load buffer zones around lakes
buffers=gpd.read_file('data/processed/lake_buffers_30m.gpkg')
print(f"Loaded {len(buffers)} buffer zones around lakes.")

# convert to lat/lon for GEE buffers_latlon is a GeoDataFrame with geometries in lat/lon (EPSG:4326)
buffers_latlon=buffers.to_crs(epsg=4326)
print("Buffer zones reprojected to lat/lon (EPSG:4326) for Earth Engine processing.")
print("Calculating mean NDBI difference for each buffer zone...")

# convert all buffer zones to GEE FeatureCollection in one go
features=[]
for idx, row in buffers_latlon.iterrows():
    geom=ee.Geometry(row.geometry.__geo_interface__)
    feature=ee.Feature(geom, {'index': idx})
    features.append(feature)
feature_collection=ee.FeatureCollection(features)

#one single GEE call to get mean NDBI difference for all buffer zones
result=ndbi_diff.reduceRegions(
    collection=feature_collection,
    reducer=ee.Reducer.mean(),
    scale=10
).getInfo()
print(result['features'][0]['properties']) #debugging print to check if 'NDBI_Diff' is present in properties
# Extract results
ndbi_values=[None]*len(buffers_latlon)  # Initialize with None for all
for feature in result['features']:
    idx=feature['properties']['index']
    ndbi_mean=feature['properties'].get('mean', None)  # Get mean NDBI difference, default to None if not present
    ndbi_values[idx]=ndbi_mean  # Assign mean NDBI difference to correct index

buffers_latlon['NDBI_Diff_Mean'] = ndbi_values
print("Mean NDBI difference calculated for all buffer zones and added to GeoDataFrame.")

valid=buffers_latlon.dropna(subset=['NDBI_Diff_Mean'])
col=valid['NDBI_Diff_Mean']
print(f"\nNDBI difference stats:")
print(f"  Min:    {col.min():.4f}")
print(f"  Max:    {col.max():.4f}")
print(f"  Mean:   {col.mean():.4f}")
print(f"  Median: {col.median():.4f}")
print(f"  Std Dev: {col.std():.4f}")

# Plot histogram
plt.figure(figsize=(10, 5))
plt.hist(col, bins=30, color="steelblue", edgecolor="black")
plt.axvline(x=0.05, color="orange", linestyle="--", label="0.05 threshold")
plt.axvline(x=0.10, color="red", linestyle="--", label="0.10 threshold")
plt.xlabel("NDBI Difference (2024 - 2019)")
plt.ylabel("Number of buffer zones")
plt.title("Distribution of NDBI Change in Lake Buffer Zones")
plt.legend()
plt.savefig("output/ndbi_distribution.png")
plt.show()
print("Histogram saved to output/ndbi_distribution.png")

#Save results before flagging
buffers_latlon.to_file('data/processed/ndbi_diff_results.gpkg', driver='GPKG')
print("NDBI difference results saved to 'data/processed/ndbi_diff_results.gpkg'.")

# Thresholds derived from statistical analysis:
# mean + 1.5 * std = 0.0041 + 1.5 * 0.0723 = 0.11 (moderate)
# mean + 2.0 * std = 0.0041 + 2.0 * 0.0723 = 0.15 (high)
THRESHOLD_MODERATE = 0.11
THRESHOLD_HIGH = 0.15

def flage_zone(value):
    if pd.isna(value):
        return "No Data"
    elif value >= THRESHOLD_HIGH:
        return "High Change"
    elif value >= THRESHOLD_MODERATE:
        return "Moderate Change"
    else:
        return "Low/No Change"

buffers_latlon['Change_Flag'] = buffers_latlon['NDBI_Diff_Mean'].apply(flage_zone)

#Summarize results
high=len(buffers_latlon[buffers_latlon['Change_Flag'] == "High Change"])
moderate=len(buffers_latlon[buffers_latlon['Change_Flag'] == "Moderate Change"])
low=len(buffers_latlon[buffers_latlon['Change_Flag'] == "Low/No Change"])

print(f"\nChange Flag Summary:")
print(f"  High Change: {high} zones")
print(f"  Moderate Change: {moderate} zones")
print(f"  Low/No Change: {low} zones")

#Save flagged results
buffers_latlon.to_file('data/processed/ndbi_diff_flagged.gpkg', driver='GPKG')
print("Flagged NDBI difference results saved to 'data/processed/ndbi_diff_flagged.gpkg'.")
