import ee

# Initialize the Earth Engine API
ee.Initialize(project="midyear-karma-484017-t7")

print("Earth Engine API initialized successfully.")

#l Test — load Sentinel-2 image collection
sentinel_2019= ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterBounds(ee.Geometry.Point([76.9558, 11.0168])) \
    .filterDate("2019-01-01", "2019-12-31") \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
print(f"Number of images found for 2019: {sentinel_2019.size().getInfo()}")

sentinel_2024= ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterBounds(ee.Geometry.Point([76.9558, 11.0168])) \
    .filterDate("2024-01-01", "2024-12-31") \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))

print(f"Number of images found for 2024: {sentinel_2024.size().getInfo()}")

#create median composites for both years
image_2019=sentinel_2019.median()
image_2024=sentinel_2024.median()
print("Median composites created for 2019 and 2024.")