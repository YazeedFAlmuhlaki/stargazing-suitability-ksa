from reusable_functions import initialize_earth_engine, get_raw_path
import ee 
import geopandas as gpd


initialize_earth_engine() 

# genral general

# print("Test 1:",ee.Number(305).getInfo()) 

# print("Test 2:", ee.Image("USGS/SRTMGL1_003").getInfo())


# per raster tests 

ksa_path = get_raw_path() / "aoi" / "saudi_arabia.gpkg"

ksa = gpd.read_file(ksa_path)

minx, miny, maxx, maxy = ksa.total_bounds
buffer_deg = 0.1
region = ee.Geometry.Rectangle([
    minx - buffer_deg,
    miny - buffer_deg,
    maxx + buffer_deg,
    maxy + buffer_deg,
])


dem_image = ee.ImageCollection("COPERNICUS/DEM/GLO30").filterBounds(region).mosaic().select("DEM")
print(dem_image.getInfo())




