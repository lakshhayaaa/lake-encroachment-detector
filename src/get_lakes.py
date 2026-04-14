import osmnx as ox

# Download raw data of lakes in Coimbatore
place="Coimbatore, Tamil Nadu, India"
tags = {'natural': 'water'}
lakes=ox.features_from_place(place, tags) #data is fetched as a GeoDataFrame with columns like 'osmid', 'name', 'geometry', etc.

print(f"Number of lakes in {place}: {len(lakes)}")
print(lakes.head())

# Save raw data as-is before any processing
lakes.to_file("data/raw/lakes_raw.gpkg", driver="GPKG")
print("Raw lake data saved to data/raw/lakes_raw.gpkg")

#Clean the data
#keep only polygon shapes - remove points and lines
lakes = lakes[lakes.geometry.geom_type == 'Polygon']
print(f"Number of polygon lakes: {len(lakes)}")

#Remove rows with null geometries
lakes=lakes[lakes.geometry.notnull()]
print(f"Number of lakes after removing null geometries: {len(lakes)}")

#Remove very small waterbodies (less than 1 hectare=10,000 sq meters)
lakes=lakes.to_crs(epsg=32644) #convert to a metres-based coordinate system for accurate area calculation
lakes=lakes[lakes.geometry.area>=10000]
print(f"Number of lakes after removing small waterbodies: {len(lakes)}")

#Reset index cleanly
lakes=lakes.reset_index(drop=True)

#Save cleaned data for future use
lakes.to_file("data/processed/lakes_cleaned.gpkg", driver="GPKG")
print("Cleaned lake data saved to data/processed/lakes_cleaned.gpkg")
