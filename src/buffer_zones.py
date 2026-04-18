import geopandas as gpd

# Load cleaned lake data
lakes=gpd.read_file('data/processed/lakes_cleaned.gpkg')
print(f"Loaded {len(lakes)} lakes from cleaned data.")

# Create 30m buffer zones around each lake
buffers=lakes.copy()
buffers['geometry']=buffers.geometry.buffer(30)
print(f"Buffer zones created with 30m radius for {len(buffers)} lakes.")

# Save buffer zones to file
buffers.to_file('data/processed/lake_buffers_30m.gpkg', driver='GPKG')
print("Buffer zones saved to 'data/processed/lake_buffers_30m.gpkg'.")