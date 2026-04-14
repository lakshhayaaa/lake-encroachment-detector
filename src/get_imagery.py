import ee

# Initialize the Earth Engine API
ee.Initialize(project="midyear-karma-484017-t7")

print("Earth Engine API initialized successfully.")

#l Test — load Sentinel-2 image collection
sentinel = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterBounds(ee.Geometry.Point([76.9558, 11.0168])) \
    .filterDate("2024-01-01", "2024-12-31") \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))

print(f"Number of images found: {sentinel.size().getInfo()}")