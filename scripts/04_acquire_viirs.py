"""
Acquire the VIIRS Day/Night Band nighttime lights composite for the AOI.

Loads the AOI from disk, builds a buffered bounding rectangle, and submits an
asynchronous Earth Engine export task that reduces the 2022-2024 annual VNL
composites into a single mean-radiance GeoTIFF. The export runs on Google's
servers and deposits the result in Google Drive; the file is then downloaded
manually into data/raw/viirs/.

VIIRS provides the artificial-light feature for the suitability model and is
the single strongest predictor of stargazing quality. Persistent anthropogenic
illumination (cities, roads, gas flares, ports) destroys night-sky observation
more than any atmospheric variable. Pixels are in nanoWatts / sr / cm^2.

Inputs
------
- data/raw/aoi/saudi_arabia.gpkg
    AOI polygon in EPSG:4326, produced by scripts/01_define_aoi.py.

- params/grid.yaml
    Reads data_source.earth_engine_project for the GEE session.

Outputs
-------
- Google Drive folder "stargazing-ksa", filename
  "viirs_avg_masked_2022_2024_ksa.tif"
    Exported by GEE asynchronously. Download manually into
    data/raw/viirs/viirs_avg_masked_2022_2024.tif after the task completes.

Notes
-----
- Dataset: NOAA/VIIRS/DNB/ANNUAL_V22, an ImageCollection with one image per
  calendar year from 2012 onward. The script filters to the 2022-2024 window,
  selects the average_masked band (per-pixel mean radiance with gas flares
  and ephemeral lights filtered out), and takes the temporal mean across
  the three years. The result is a single image representing typical
  persistent radiance at each pixel.

- Three-year averaging reduces year-to-year noise from transient industrial
  activity (one-off flares, construction lighting, brief outages) while
  keeping the composite representative of current conditions.

- Native resolution is ~464 m, but the export is scaled to 1000 m to match
  the project grid. Aggregation on GEE's servers (mean reducer, applied
  automatically) is cheaper than downloading native-resolution data and
  resampling locally.

- Native CRS is EPSG:4326. The export preserves the CRS. Reprojection to
  the project CRS (EPSG:8857) happens in Phase 4.

- A 0.1 degree buffer (~11 km) is added to the AOI bounds. Same rationale
  as the DEM script.

- ee.batch.Export.image.toDrive is asynchronous. The script kicks off the
  task and exits immediately. Monitor progress at
  https://code.earthengine.google.com/tasks.

"""

import ee 
import geopandas as gpd
from reusable_functions import initialize_earth_engine, get_raw_path 
 

def submit_viirs_export():

    initialize_earth_engine()

    ksa_path = get_raw_path() / "aoi" / "saudi_arabia.gpkg"

    ksa = gpd.read_file(ksa_path)

    minx, miny, maxx, maxy = ksa.total_bounds 
    buffer = 0.1

    region = ee.Geometry.Rectangle([
            minx - buffer, 
            miny - buffer, 
            maxx + buffer, 
            maxy + buffer
    ])

    virrs_image = (

        ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22")
        .filterDate("2022-01-01", "2025-01-01")
        .filterBounds(region)
        .select("average_masked")
        .mean()

    )

    task = ee.batch.Export.image.toDrive(
        image = virrs_image, 
        description = "viirs_avg_masked_2022_2024_ksa", 
        folder = "stargazing-ksa",
        region = region, 
        scale = 1000, 
        crs = "EPSG:4326", 
        maxPixels=1e10,
        fileFormat="GeoTIFF"
    )   

    task.start()

    print("Export task started.")
    print("Task ID:", task.id)
    print("Status:", task.status())


if __name__ == "__main__": 
    submit_viirs_export()


