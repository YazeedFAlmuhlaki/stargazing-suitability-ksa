"""
Acquire the Copernicus GLO-30 Digital Elevation Model for the AOI.

Loads the AOI from disk, builds a buffered bounding rectangle, and submits an
asynchronous Earth Engine export task that mosaics all GLO-30 tiles intersecting
Saudi Arabia into a single GeoTIFF. The export runs on Google's servers and
deposits the result in Google Drive; the file is then downloaded manually into
data/raw/dem/.

The DEM contributes the elevation feature to the suitability model. Higher
elevation corresponds to a thinner atmospheric column, which slightly improves
stargazing conditions through reduced Rayleigh scattering and shorter optical
pathlength through aerosol layers.

Inputs
------
- data/raw/aoi/saudi_arabia.gpkg
    AOI polygon in EPSG:4326, produced by scripts/01_define_aoi.py.

- params/grid.yaml
    Reads data_source.earth_engine_project for the GEE session.

Outputs
-------
- Google Drive folder "stargazing-ksa", filename "dem_copernicus_glo30_ksa.tif"
    Exported by GEE asynchronously. Download manually into
    data/raw/dem/copernicus_glo30.tif after the task completes.

Notes
-----
- Dataset: COPERNICUS/DEM/GLO30, an ImageCollection of 1 degree tiles. The
  script filters to tiles intersecting the AOI (~364 tiles for Saudi Arabia),
  mosaics them, and selects only the DEM band (auxiliary masks EDM, FLM, HEM,
  WBM are discarded).

- Native CRS is EPSG:4326 at 30 m resolution. The export preserves the CRS
  while scaling to 1000 m. Reprojection to the project CRS (EPSG:8857)
  happens in Phase 4. Keeping the raw acquisition in source CRS avoids
  double-reprojection and gives us control over the resampling method later.

- Native resolution is 30 m, but the export is scaled to 1000 m to match
  the project grid. Aggregating on GEE's servers (mean reducer, applied
  automatically) is cheaper than downloading ~14 GB and resampling locally
  to a 1 km grid we never use the sub-kilometre detail of.

- A 0.1 degree buffer (~11 km) is added to the AOI bounds. This is
  independent of the 5 km grid buffer from Phase 1; the two buffers exist
  for the same reason (protecting against resampling edge effects) but
  apply at different stages.

- ee.batch.Export.image.toDrive is asynchronous. The script kicks off the
  task and exits immediately. Monitor progress at
  https://code.earthengine.google.com/tasks.
"""

import ee 
import geopandas as gpd
from reusable_functions import initialize_earth_engine, get_raw_path 




def submit_dem_export(): 

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

    dem_image = ee.ImageCollection("COPERNICUS/DEM/GLO30").filterBounds(region).mosaic().select("DEM")

    task = ee.batch.Export.image.toDrive(
        image = dem_image, 
        description = "dem_copernicus_glo30_ksa", 
        folder = "stargazing-ksa", 
        region=region,
        scale=1000,
        crs="EPSG:4326",
        maxPixels=1e10,
        fileFormat="GeoTIFF"
    )

    task.start()

    print("Export task started.")
    print("Task ID:", task.id)
    print("Status:", task.status())


if __name__ == "__main__":
    submit_dem_export() 