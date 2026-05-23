"""
All reused functions will be defined in this file
"""


import duckdb 
from pathlib import Path
import yaml
import ee


ROOT_PATH = Path(__file__).parent.parent 





def start_duckdb_connection () -> duckdb.DuckDBPyConnection: 
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


def initialize_earth_engine():
    """"""

    params = load_grid_params()

    gee_pid = params["data_source"]["earth_engine_project"]

    ee.Authenticate()

    ee.Initialize(project = gee_pid)


    


def get_raw_path(): 
    """returns a path to raw folder"""
    return ROOT_PATH / "data" / "raw"



def load_grid_params():
    """returens the parameter defined for the project"""

    yaml_path = ROOT_PATH / "params" / "grid.yaml"

    with open(yaml_path) as pram: 
        data = yaml.safe_load(pram)
    
    return data


def save_grid_params(params): 
    """overwriting our yaml file with the passed parameters"""

    yaml_path = ROOT_PATH / "params" / "grid.yaml"

    with open(yaml_path, "w") as f: 
        yaml.safe_dump(params, f, sort_keys= False, default_flow_style= False)
        