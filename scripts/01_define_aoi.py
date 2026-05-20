"""
Define the Area of Interest (AOI) for the stargazing suitability pipeline.

Queries the Overture Maps `divisions` theme via DuckDB and extracts the
national boundary polygon for Saudi Arabia (country code 'SA', subtype
'country', land geometry only). The result is saved as a GeoPackage and
serves as the spatial reference for all downstream pipeline stages.

Inputs
------
- Overture Maps release specified in `params/grid.yaml`
  (data_sources.overture_release).
- Hosted on s3://overturemaps-us-west-2/release/<release>/theme=divisions/
  type=division_area/

Outputs
-------
- data/raw/aoi/saudi_arabia.gpkg
    Single-feature GeoPackage in EPSG:4326. Attributes: id, name, country.
"""

import geopandas as gpd 
import matplotlib.pyplot as plt
from reusable_functions import start_connection, get_raw_path, get_params


# get all defined parameters
parameter = get_params()

# get the aoi url path
divisions_s3_path = parameter["data_source"]["aoi_path"]


def acquire_poi() -> gpd.GeoDataFrame: 
    """
    This function return the ksa boundry without saving any files
    """

    con = start_connection() 

    sql = f"""
        SELECT 
             id, 
             names.primary as name, 
             country, 
             ST_AsWKB(geometry) as geometry 
        FROM read_parquet('{divisions_s3_path}*')
        WHERE country = 'SA' 
        AND is_land = True
        AND subtype = 'country'; 
        """
    
    ksa_df = con.sql(sql).fetchdf() 

    # The .apply(bytes) method iterates through every row of geometry column and converts each individual bytearray into an immutable bytes object.
    geometries = gpd.GeoSeries.from_wkb(ksa_df["geometry"].apply(bytes))

    ksa_gdf = gpd.GeoDataFrame(ksa_df.drop(columns = ["geometry"]), 
                               geometry=geometries,
                               crs="EPSG:4326")

    return ksa_gdf


def save_aoi(): 
    """
    function used to save aoi as geopackage
    """

    ksa_gdf = acquire_poi()

    raw_path= get_raw_path()
    aoi_path = raw_path / "aoi" / "saudi_arabia.gpkg"
    aoi_path.parent.mkdir(parents=True, exist_ok=True)

    ksa_gdf.to_file(aoi_path, driver="GPKG")
    print(f"saudi arabia file saved into {aoi_path}")

    print(f"Reading {aoi_path} ...")
    gdf = gpd.read_file(aoi_path)
    
    print("Columns:", gdf.columns.to_list())
    print("Data Count:", len(gdf))
    print("Name:", gdf.name.values[0])
    print("Bounding Box:", gdf.bounds.values)
    print("Total Area:", gdf.to_crs("EPSG:32638").geometry.area.iloc[0] / 1e6)

    print("All Done ...")
    
    




    
if __name__ == "__main__":
    save_aoi()
