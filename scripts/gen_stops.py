#!/usr/bin/env python3
# Get stops from geojson

import os
import uuid
import geopandas as gpd
import pprint

script_dir = os.path.dirname(os.path.realpath(__file__))

gdf = gpd.read_file(f"{script_dir}/ellsworth_stops.geojson")
gdf["stop_id"] = [f"STOP-{uuid.uuid4()}" for _ in range(len(gdf.index))]
STOPS = list(gdf.apply(lambda row: {
      "stop_id": row.stop_id,
      "stop_name": row.stop_name,
      "stop_desc": row.stop_desc,
      "stop_lat": row.geometry.x,
      "stop_lon": row.geometry.y,
}, axis=1))
pprint.pprint(STOPS)
