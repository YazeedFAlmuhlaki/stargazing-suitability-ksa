"""
All reused functions will be defined in this file
"""


import duckdb 
from pathlib import Path
import yaml


def start_connection() -> duckdb.DuckDBPyConnection: 
    """start duckdb connection"""

    con = duckdb.connect()

    extensions = ["httpfs", "spatial"]

    for ext in extensions: 
        con.install_extension(ext)
        con.load_extension(ext)
    
    """
    Configure anonymous S3 access. Overture's bucket is public, but DuckDB's default 
    credential lookup chain may pick up stray AWS credentials from the environment 
    and fail. An explicit empty-credential secret forces anonymous mode.
    """
    con.execute("""
    CREATE OR REPLACE SECRET (
        TYPE s3,
        PROVIDER config,
        KEY_ID '',
        SECRET '',
        REGION 'us-west-2'
    );
                """)

    return con


def get_raw_path(): 
    """returns a path to raw folder"""
    return Path("data/raw")

def load_grid_params():
    """returens the parameter defined for the project"""

    with open("params/grid.yaml") as pram: 
        data = yaml.safe_load(pram)
    
    return data


def save_grid_params(params): 
    """overwriting our yaml file with the passed parameters"""

    with open("params/grid.yaml", "w") as f: 
        yaml.safe_dump(params, f, sort_keys= False, default_flow_style= False)
        

