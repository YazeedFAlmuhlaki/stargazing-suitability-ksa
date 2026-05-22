"""
Define the master computational grid for the stargazing suitability pipeline.

Ingests the Area of Interest (AOI) geometry produced by 01_define_aoi.py and computes
a reproducible bounding box in the project CRS. Bounds are rounded outward to clean
multiples of the cell size, then expanded by a buffer to accommodate reprojection
edge effects in later phases. The resulting grid origin and dimensions are written
back to params/grid.yaml, where every downstream script reads them. This is what
guarantees that VIIRS, MODIS, CAMS, DEM, and the distance rasters all align
pixel-for-pixel in the feature matrix.

Inputs
------
- data/raw/aoi/saudi_arabia.gpkg
    AOI polygon in EPSG:4326, produced by scripts/01_define_aoi.py.

- params/grid.yaml
    Reads crs, cell_size_m, and buffer_cells. The remaining grid fields
    are written by this script.

Outputs
-------
- params/grid.yaml (updated)
    Populates origin_x, origin_y, n_cols, n_rows from the computed bounds.

Notes
-----
- CRS is EPSG:8857 (Equal Earth) rather than UTM 38N. Saudi Arabia spans
  21 degrees of longitude, far more than a UTM zone's 6-degree validity
  band. Equal Earth is equal-area, metric, and globally defined.

- Bounds are rounded outward (math.floor for min, math.ceil for max), then
  buffered by buffer_cells * cell_size_m on every side. Two reasons: clean
  numbers eliminate floating-point drift across re-runs, and the buffer
  ensures resampling kernels at the AOI boundary always find valid neighbours.

- The grid origin follows raster convention: (origin_x, origin_y) is the
  top-left corner of the top-left cell, i.e. (minx_final, maxy_final).

"""


from math import ceil, floor 
import geopandas as gpd 
from reusable_functions import load_grid_params, save_grid_params, get_raw_path


params = load_grid_params()
AOI_PATH = get_raw_path() / "aoi" / "saudi_arabia.gpkg"

def compute_and_save_grid(): 
    """"""

    aoi_gdf = gpd.read_file(AOI_PATH)
    aoi_gdf.to_crs(params["crs"], inplace=True)

    cell_size = params["cell_size_m"]
    buffer_cells = params["buffer_cells"]
    buffer_m = buffer_cells * cell_size 

    bbox = aoi_gdf.total_bounds # [minx, miny, maxx, maxy]

    minx, miny, maxx, maxy = bbox

    minx_round = floor(minx / cell_size) * cell_size
    maxx_round = ceil(maxx /  cell_size) * cell_size

    miny_round = floor(miny / cell_size) * cell_size
    maxy_round = ceil(maxy / cell_size)  * cell_size

    minx_final = minx_round - buffer_m
    maxx_final = maxx_round + buffer_m

    miny_final = miny_round - buffer_m 
    maxy_final = maxy_round + buffer_m

    n_cols = int((maxx_final - minx_final) / cell_size)
    n_rows = int((maxy_final - miny_final) / cell_size)

    params["origin_x"] = minx_final
    params["origin_y"] = maxy_final

    params["n_cols"] = n_cols
    params["n_rows"] = n_rows 

    save_grid_params(params=params)

    read_new_params = load_grid_params()

    print("SUMMRAY:")

    print("final minimum x:", minx_final)
    print("final minimum y:", miny_final)
    print("final maximum x:", maxx_final)
    print("final maximum y:", maxy_final)

    print("origin_x:", read_new_params["origin_x"])
    print("origin_y:", read_new_params["origin_y"])

    print(f"Dimensions (n_rows * n_cols):{read_new_params["n_rows"]}*{read_new_params["n_cols"]}")
    
    print("Total Cells:", read_new_params["n_cols"]*read_new_params["n_rows"])

    print("Approximate memory footprint of a single float32 raster:", read_new_params["n_rows"] * read_new_params["n_cols"] * 4 / (1024**2), "MB")
   

if __name__ == "__main__":
    compute_and_save_grid()









