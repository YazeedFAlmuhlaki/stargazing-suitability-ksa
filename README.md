# Stargazing Suitability Modeling for Saudi Arabia

An unsupervised geospatial machine learning pipeline that produces a 1 km
stargazing suitability raster for the territory of Saudi Arabia and ranks
the most promising candidate sites for astronomical observation and
astrotourism development.

The pipeline combines satellite, atmospheric, and vector data — VIIRS
nighttime lights, MODIS cloud climatology, CAMS aerosol optical depth,
Copernicus DEM elevation, and Overture Maps road and settlement layers —
into a single feature space. Cells are scored using two complementary
unsupervised methods: an averaged z-score across standardised features,
and an isolation-forest anomaly score that identifies cells unusually
favourable relative to the Saudi baseline. The top fifty accessible
candidate sites are exported as a GeoPackage with full attribution.

## Repository layout

```
stargazing-suitability-ksa/
├── data/
│   ├── raw/          # untouched downloads from each source
│   ├── interim/      # single-band GeoTIFFs after reprojection
│   └── processed/    # final feature stack, suitability rasters, candidates
├── notebooks/        # exploration and sanity-check maps
├── src/              # reusable modules (config loading, I/O helpers)
├── scripts/          # numbered pipeline steps, run in order
├── params/
│   └── grid.yaml     # single source of truth for spatial parameters
├── reports/          # validation figures and narrative report
├── pyproject.toml
└── README.md
```

## Status

In development

## Data sources

See the project specification document for full attribution. Primary
sources are VIIRS DNB (Earth Observation Group, Colorado School of Mines),
MODIS atmosphere products (NASA), CAMS reanalysis (Copernicus / ECMWF),
Copernicus GLO-30 DEM, and Overture Maps Foundation.

## License

Code released under the MIT License. Input data and derived products
inherit licences from their respective sources.