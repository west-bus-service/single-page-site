#!/usr/bin/env python3

import os
import shutil
import tempfile
from enum import Enum
from pathlib import Path

import pandas as pd

script_dir = os.path.dirname(os.path.realpath(__file__))
feed_path = Path(script_dir).parent / "west_gtfs"


class RouteTypes(Enum):
    TRAM = 0  # Tram, Streetcar, Light rail. Any light rail or street level system within a metropolitan area.
    SUBWAY = 1  # Subway, Metro. Any underground rail system within a metropolitan area.
    RAIL = 2  # Rail. Used for intercity or long-distance travel.
    BUS = 3  # Bus. Used for short- and long-distance bus routes.
    FERRY = 4  # Ferry. Used for short- and long-distance boat service.
    CABLE = 5  # Cable tram. Used for street-level rail cars where the cable runs beneath the vehicle (e.g., cable car in San Francisco).
    AERIAL = 6  # Aerial lift, suspended cable car (e.g., gondola lift, aerial tramway). Cable transport where cabins, cars, gondolas or open chairs are suspended by means of one or more cables.
    FUNICULAR = 7  # Funicular. Any rail system designed for steep inclines.
    TROLLEY = 11  # Trolleybus. Electric buses that draw power from overhead wires using poles.
    MONORAIL = (
        12  # Monorail. Railway in which the track consists of a single rail or a beam.
    )


class DirectionId(Enum):
    OUTBOUND = 0  # Travel in one direction (e.g. outbound travel).
    INBOUND = 1  # Travel in the opposite direction (e.g. inbound travel).


class BikesAllowed(Enum):
    UNKNOWN = 0  # No bike information for the trip.
    YES = 1  # Vehicle being used on this particular trip can accommodate at least one bicycle.
    NO = 2  # No bicycles are allowed on this trip.


class ServiceAvailable(Enum):
    YES = 1  # Service is available
    NO = 0  # Service is not available


AGENCY_ID = "WT"
WEST_COASTAL_CONNECTION_ID = "WCC"

AGENCY = {
    # Agency Id
    "agency_id": AGENCY_ID,
    # Agency Name
    "agency_name": "West's Transportation",
    # Agency URL
    "agency_url": "https://westbusservice.com",
    # Agency Timezone
    "agency_timezone": "America/New_York",
}

FEED_INFO = {
    "feed_publisher_name": AGENCY["agency_name"],
    "feed_publisher_url": AGENCY["agency_url"],
    "feed_contact_email": "westbus@ymail.com",
    "feed_contact_url": AGENCY["agency_url"],
    "feed_lang": "en-US",
    "feed_version": 1,
    "feed_start_date": 20241121,
    "feed_end_date": 20251121,
}

ROUTES = [
    {
        "route_id": WEST_COASTAL_CONNECTION_ID,
        "agency_id": AGENCY_ID,
        "route_short_name": WEST_COASTAL_CONNECTION_ID,
        "route_long_name": "West's Coastal Connection",
        "route_desc": "Daily public bus service from Calais to Bangor and points in between",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
]

TRIPS = [
    {
        "route_id": WEST_COASTAL_CONNECTION_ID,
        "service_id": "daily",
        "trip_id": "WCCWB",
        "trip_short_name": "Bangor (via Rt 1)",
        "direction_id": DirectionId.INBOUND.value,
        # "shape_id": "",  # TODO: shapes.shape_id
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("09:30", "STOP-9034671c-e991-4439-9e71-a05a8599a56f"),
            ("10:00", "STOP-14ed8aff-0f08-4ac4-89fe-e9b172db07bb"),
            ("10:10", "STOP-2ad237c0-4dfe-4a50-a8cd-cec8972e1922"),
            ("10:15", "STOP-c48d97aa-f7b1-4560-b697-048d4aca8f74"),
            ("10:25", "STOP-d530cc40-12bd-4071-95de-52fbaf1d7d23"),
            ("11:00", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
            ("11:10", "STOP-3186da65-c835-47ae-9095-f3881148ffc9"),
            ("11:20", "STOP-be554e9d-f180-450f-902b-a772328ac4dd"),
            ("11:35", "STOP-7a5a3410-4d73-4cbf-aea1-df3d4aa243f2"),
            ("11:55", "STOP-e354cfda-7054-4ed6-b5c4-e7a4975cfdbd"),
            ("12:05", "STOP-970a9e30-06d7-4ddb-98cc-49cdee5588cb"),
            ("12:10", "STOP-fc0ebfb0-a667-4382-88d3-d3f194bf26b6"),
            ("12:25", "STOP-2cd4673a-e3d0-472f-9654-37a6c9233e4a"),
            ("13:10", "STOP-3012643a-132d-4c0d-974e-cdc8714f9368"),
            ("13:15", "STOP-8f56e854-d898-49f8-aef1-f6420a0c6042"),
        ],
    },
    {
        "route_id": WEST_COASTAL_CONNECTION_ID,
        "service_id": "daily",
        "trip_id": "WCCEB",
        "trip_short_name": "Calais (via Rt 1)",
        "direction_id": DirectionId.OUTBOUND.value,
        # "shape_id": "",  # TODO: shapes.shape_id
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("14:00", "STOP-3012643a-132d-4c0d-974e-cdc8714f9368"),
            ("14:10", "STOP-8f56e854-d898-49f8-aef1-f6420a0c6042"),
            ("14:45", "STOP-2cd4673a-e3d0-472f-9654-37a6c9233e4a"),
            ("15:20", "STOP-fc0ebfb0-a667-4382-88d3-d3f194bf26b6"),
            ("15:25", "STOP-970a9e30-06d7-4ddb-98cc-49cdee5588cb"),
            ("15:35", "STOP-e354cfda-7054-4ed6-b5c4-e7a4975cfdbd"),
            ("15:50", "STOP-7a5a3410-4d73-4cbf-aea1-df3d4aa243f2"),
            ("16:05", "STOP-be554e9d-f180-450f-902b-a772328ac4dd"),
            ("16:20", "STOP-3186da65-c835-47ae-9095-f3881148ffc9"),
            ("16:30", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
            ("16:50", "STOP-d530cc40-12bd-4071-95de-52fbaf1d7d23"),
            ("17:10", "STOP-c48d97aa-f7b1-4560-b697-048d4aca8f74"),
            ("17:20", "STOP-2ad237c0-4dfe-4a50-a8cd-cec8972e1922"),
            ("17:30", "STOP-14ed8aff-0f08-4ac4-89fe-e9b172db07bb"),
            ("18:00", "STOP-9034671c-e991-4439-9e71-a05a8599a56f"),
        ],
    },
]

# Get stops from geojson
# gdf = gpd.read_file("gtfs/stops.geojson")
# gdf["stop_id"] = [f"STOP-{uuid.uuid4()}" for _ in range(len(gdf.index))]
# STOPS = list(gdf.apply(lambda row: {
#       "stop_id": row.stop_id,
#       "stop_name": row.stop_name,
#       "stop_desc": row.stop_desc,
#       "stop_lat": row.geometry.x,
#       "stop_lon": row.geometry.y,
# }, axis=1))
STOPS = [
    {
        "stop_id": "STOP-9034671c-e991-4439-9e71-a05a8599a56f",
        "stop_name": "Calais",
        "stop_desc": "Marden's Parking Lot",
        "stop_lat": -67.28220840306957,
        "stop_lon": 45.18854669392266,
    },
    {
        "stop_id": "STOP-14ed8aff-0f08-4ac4-89fe-e9b172db07bb",
        "stop_name": "Perry",
        "stop_desc": "Wabanaki Mall",
        "stop_lat": -67.07493005575536,
        "stop_lon": 44.97231404736198,
    },
    {
        "stop_id": "STOP-2ad237c0-4dfe-4a50-a8cd-cec8972e1922",
        "stop_name": "Pembroke",
        "stop_desc": "Corner of Rt. 214 & Rt. 1",
        "stop_lat": -67.17868296829499,
        "stop_lon": 44.949701161833104,
    },
    {
        "stop_id": "STOP-c48d97aa-f7b1-4560-b697-048d4aca8f74",
        "stop_name": "Dennysville",
        "stop_desc": "Cobscook Bay Cafe",
        "stop_lat": -67.22544494819728,
        "stop_lon": 44.908957562098266,
    },
    {
        "stop_id": "STOP-d530cc40-12bd-4071-95de-52fbaf1d7d23",
        "stop_name": "Whiting",
        "stop_desc": "Community Center/Store",
        "stop_lat": -67.17424929425094,
        "stop_lon": 44.791233559261826,
    },
    {
        "stop_id": "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10",
        "stop_name": "Machias",
        "stop_desc": "Irving Mainway",
        "stop_lat": -67.45320159645519,
        "stop_lon": 44.71747416614576,
    },
    {
        "stop_id": "STOP-3186da65-c835-47ae-9095-f3881148ffc9",
        "stop_name": "Jonesboro",
        "stop_desc": "Swamp Yankee BBQ",
        "stop_lat": -67.57294144907351,
        "stop_lon": 44.662060972756706,
    },
    {
        "stop_id": "STOP-be554e9d-f180-450f-902b-a772328ac4dd",
        "stop_name": "Columbia",
        "stop_desc": "Elmer\u2019s Discount",
        "stop_lat": -67.76299771361364,
        "stop_lon": 44.64287175736857,
    },
    {
        "stop_id": "STOP-7a5a3410-4d73-4cbf-aea1-df3d4aa243f2",
        "stop_name": "Milbridge",
        "stop_desc": "44 North Rest.",
        "stop_lat": -67.88149880431949,
        "stop_lon": 44.537812397946055,
    },
    {
        "stop_id": "STOP-e354cfda-7054-4ed6-b5c4-e7a4975cfdbd",
        "stop_name": "Gouldsboro",
        "stop_desc": "Young's Market",
        "stop_lat": -68.1149969959795,
        "stop_lon": 44.484226237813715,
    },
    {
        "stop_id": "STOP-970a9e30-06d7-4ddb-98cc-49cdee5588cb",
        "stop_name": "Sullivan",
        "stop_desc": "Sullivan REC. Center",
        "stop_lat": -68.22476574771778,
        "stop_lon": 44.53024290489276,
    },
    {
        "stop_id": "STOP-fc0ebfb0-a667-4382-88d3-d3f194bf26b6",
        "stop_name": "Hancock",
        "stop_desc": "Village Store",
        "stop_lat": -68.25858959486574,
        "stop_lon": 44.53014123436881,
    },
    {
        "stop_id": "STOP-2cd4673a-e3d0-472f-9654-37a6c9233e4a",
        "stop_name": "Hancock",
        "stop_desc": "Main Entrance Mill Mall, Out Back",
        "stop_lat": -68.43000587506339,
        "stop_lon": 44.551403972284845,
    },
    {
        "stop_id": "STOP-3012643a-132d-4c0d-974e-cdc8714f9368",
        "stop_name": "Bangor (Concord Trailways)",
        "stop_desc": "Concord Trailways",
        "stop_lat": -68.80876371853913,
        "stop_lon": 44.816594110637595,
    },
    {
        "stop_id": "STOP-8f56e854-d898-49f8-aef1-f6420a0c6042",
        "stop_name": "Bangor (Airport)",
        "stop_desc": "Bangor Airport",
        "stop_lat": -68.81786055142301,
        "stop_lon": 44.80905167866493,
    },
]

CALENDAR = [
    {
        "service_id": "daily",
        "monday": ServiceAvailable.YES.value,
        "tuesday": ServiceAvailable.YES.value,
        "wednesday": ServiceAvailable.YES.value,
        "thursday": ServiceAvailable.YES.value,
        "friday": ServiceAvailable.YES.value,
        "saturday": ServiceAvailable.YES.value,
        "sunday": ServiceAvailable.YES.value,
        "start_date": 20241121,
        "end_date": 20251121,
    }
]

FILES = {
    "agency.txt": [AGENCY],
    "stops.txt": STOPS,
    "routes.txt": ROUTES,
    "trips.txt": [
        {k: v for k, v in trip.items() if k != "stop_times"} for trip in TRIPS
    ],
    "stop_times.txt": [
        item
        for sublist in [
            [
                {
                    "trip_id": trip["trip_id"],
                    "arrival_time": f"{time}:00",
                    "departure_time": f"{time}:00",
                    "stop_id": stop_id,
                    "stop_sequence": i,
                }
                for i, (time, stop_id) in enumerate(trip["stop_times"])
            ]
            for trip in TRIPS
        ]
        for item in sublist
    ],
    "calendar.txt": CALENDAR,
    "feed_info.txt": [FEED_INFO],
}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdirname:
        for filename, data in FILES.items():
            pd.DataFrame(data).to_csv(Path(tmpdirname) / filename, index=False)
        shutil.make_archive(str(feed_path), "zip", tmpdirname)
