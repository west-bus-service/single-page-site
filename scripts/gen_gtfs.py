#!/usr/bin/env python3

import calendar
import os
import shutil
import tempfile
import json
import geojson
from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd

script_dir = os.path.dirname(os.path.realpath(__file__))
feed_path = Path(script_dir).parent / "west_gtfs"

now = datetime.now()


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


class ServiceException(Enum):
    ADDED = 1  # Service is added
    REMOVED = 2  # Service is removed


def _coords(fp):
    """Helper to open fp and return its first feature’s LineString coords."""
    with open(fp, "r", encoding="utf-8") as f:
        fc = geojson.load(f)
    return fc.features[0].geometry.coordinates


AGENCY_ID = "WT"
AGENCY_EMAIL = "westbus@ymail.com"
WEST_COASTAL_CONNECTION_ID = "WCC"
ELLSWORTH_ROUTE_ID = "ELLS"
MACHIAS_ROUTE_ID = "MACH"
WEEKDAY_ROUTE_ID = "WEEK"
LUBEC_ROUTE_ID = "LBC"
SCHOOL_ROUTE_ID = "SCHL"
DAILY_SERVICE_ID = "DAILY"
WEEKDAY_SERVICE_ID = "WEEKDAY"
MONDAY_SERVICE_ID = "MONDAY"
TUESDAY_SERVICE_ID = "TUESDAY"
FW_OF_MONTH_SERVICE_ID = "FW"
SCHOOL_SERVICE_ID = "SCHL"

AGENCY = {
    # Agency Id
    "agency_id": AGENCY_ID,
    # Agency Name
    "agency_name": "West's Transportation",
    # Agency URL
    "agency_url": "https://westbusservice.com",
    # Agency Timezone
    "agency_timezone": "America/New_York",
    "agency_phone": "207-546-2823",
    "agency_email": AGENCY_EMAIL,
}

FEED_START = 20250723
FEED_END = 20271231

FEED_INFO = {
    "feed_publisher_name": AGENCY["agency_name"],
    "feed_publisher_url": AGENCY["agency_url"],
    "feed_contact_email": AGENCY_EMAIL,
    "feed_contact_url": AGENCY["agency_url"],
    "feed_lang": "en-US",
    "feed_version": 1,
    "feed_start_date": FEED_START,
    "feed_end_date": FEED_END,
}

ROUTES = [
    {
        "route_id": WEST_COASTAL_CONNECTION_ID,
        "agency_id": AGENCY_ID,
        "route_long_name": "West's Coastal Connection",
        "route_desc": "Daily public bus service from Calais to Bangor and points in between",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
    {
        "route_id": ELLSWORTH_ROUTE_ID,
        "agency_id": AGENCY_ID,
        "route_long_name": "Monday Bus to Ellsworth",
        "route_desc": "Monday service from Beals Island to Ellsworth",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
    {
        "route_id": MACHIAS_ROUTE_ID,
        "agency_id": AGENCY_ID,
        "route_long_name": "Tuesday Bus to Machias",
        "route_desc": "Tuesday service from Steuben to Machias",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
    {
        "route_id": WEEKDAY_ROUTE_ID,
        "agency_id": AGENCY_ID,
        "route_long_name": "Steuben to Jonesport",
        "route_desc": "Weekday service from Steuben to Jonesport",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
    {
        "route_id": LUBEC_ROUTE_ID,
        "agency_id": AGENCY_ID,
        "route_long_name": "Lubec to Machias",
        "route_desc": "First Wednesday of the month service from Lubec to Machias",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
    {
        "route_id": SCHOOL_ROUTE_ID,
        "agency_id": AGENCY_ID,
        "route_long_name": "Franklin to Winter Harbor",
        "route_desc": "Weekday service during the school season from Franklin to Winter Harbor",
        "route_type": RouteTypes.BUS.value,
        # "route_url": "",
        # "route_color": "",
        # "route_text_color": "",
    },
]

TRIPS = [
    {
        "route_id": WEST_COASTAL_CONNECTION_ID,
        "service_id": DAILY_SERVICE_ID,
        "trip_id": "WCCWB",
        "direction_id": DirectionId.INBOUND.value,
        "shape_id": "WCCWB",
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
        "service_id": DAILY_SERVICE_ID,
        "trip_id": "WCCEB",
        "direction_id": DirectionId.OUTBOUND.value,
        "shape_id": "WCCEB",
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
    {
        "route_id": ELLSWORTH_ROUTE_ID,
        "service_id": MONDAY_SERVICE_ID,
        "trip_id": "ELLSWB",
        "direction_id": DirectionId.OUTBOUND.value,
        "shape_id": "ELLSWB",
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("08:30", "STOP-b11bb36f-65f5-4bfe-abb8-bdf1d76ac3b9"),
            ("08:35", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
            ("09:00", "STOP-709e5965-7b27-4c47-a1de-1eedbea4350e"),
            ("09:05", "STOP-fc77e641-ea79-4e44-b050-16cf14331355"),
            ("09:10", "STOP-a8fb5add-97f2-4284-8533-1f2181fdc6f8"),
            ("09:15", "STOP-a64ef87a-091d-47ea-9c17-8f1652e1d882"),
            ("09:25", "STOP-fc06a983-3770-4ca9-882e-4b90cd0c3573"),
            ("09:35", "STOP-d6a9c3c6-72f3-47fb-9317-bd223cbd3764"),
            ("09:40", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
            ("10:30", "STOP-14ae1c74-7f7c-4204-be30-265e030a1c35"),
        ],
    },
    {
        "route_id": ELLSWORTH_ROUTE_ID,
        "service_id": MONDAY_SERVICE_ID,
        "trip_id": "ELLSEB",
        "direction_id": DirectionId.INBOUND.value,
        "shape_id": "ELLSEB",
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("13:30", "STOP-14ae1c74-7f7c-4204-be30-265e030a1c35"),
            ("14:05", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
            ("14:10", "STOP-d6a9c3c6-72f3-47fb-9317-bd223cbd3764"),
            ("14:20", "STOP-fc06a983-3770-4ca9-882e-4b90cd0c3573"),
            ("14:30", "STOP-a64ef87a-091d-47ea-9c17-8f1652e1d882"),
            ("14:35", "STOP-a8fb5add-97f2-4284-8533-1f2181fdc6f8"),
            ("14:40", "STOP-fc77e641-ea79-4e44-b050-16cf14331355"),
            ("14:45", "STOP-709e5965-7b27-4c47-a1de-1eedbea4350e"),
            ("15:00", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
            ("15:05", "STOP-b11bb36f-65f5-4bfe-abb8-bdf1d76ac3b9"),
        ],
    },
    {
        "route_id": MACHIAS_ROUTE_ID,
        "service_id": TUESDAY_SERVICE_ID,
        "trip_id": "MACHEB",
        "direction_id": DirectionId.OUTBOUND.value,
        "shape_id": "MACHEB",
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("08:15", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
            ("08:20", "STOP-d6a9c3c6-72f3-47fb-9317-bd223cbd3764"),
            ("08:25", "STOP-fc06a983-3770-4ca9-882e-4b90cd0c3573"),
            ("08:30", "STOP-a64ef87a-091d-47ea-9c17-8f1652e1d882"),
            ("08:35", "STOP-a8fb5add-97f2-4284-8533-1f2181fdc6f8"),
            ("08:40", "STOP-fc77e641-ea79-4e44-b050-16cf14331355"),
            ("08:45", "STOP-709e5965-7b27-4c47-a1de-1eedbea4350e"),
            ("09:00", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
            ("09:30", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
        ],
    },
    {
        "route_id": MACHIAS_ROUTE_ID,
        "service_id": TUESDAY_SERVICE_ID,
        "trip_id": "MACHWB",
        "direction_id": DirectionId.INBOUND.value,
        "shape_id": "MACHWB",
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            # ORIGINAL from online
            # ("12:00", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
            # ("12:30", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
            # ("12:35", "STOP-709e5965-7b27-4c47-a1de-1eedbea4350e"),
            # ("12:55", "STOP-fc77e641-ea79-4e44-b050-16cf14331355"),
            # ("13:00", "STOP-a8fb5add-97f2-4284-8533-1f2181fdc6f8"),
            # ("13:30", "STOP-a64ef87a-091d-47ea-9c17-8f1652e1d882"),
            # ("13:15", "STOP-fc06a983-3770-4ca9-882e-4b90cd0c3573"),
            # ("13:30", "STOP-d6a9c3c6-72f3-47fb-9317-bd223cbd3764"),
            # ("13:35", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
            # MODIFIED for realism
            ("12:00", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
            ("12:30", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
            ("12:45", "STOP-709e5965-7b27-4c47-a1de-1eedbea4350e"),
            ("12:55", "STOP-fc77e641-ea79-4e44-b050-16cf14331355"),
            ("13:00", "STOP-a8fb5add-97f2-4284-8533-1f2181fdc6f8"),
            # TODO: Ask why this stop time is incorrect online
            ("13:10", "STOP-a64ef87a-091d-47ea-9c17-8f1652e1d882"),
            ("13:15", "STOP-fc06a983-3770-4ca9-882e-4b90cd0c3573"),
            ("13:30", "STOP-d6a9c3c6-72f3-47fb-9317-bd223cbd3764"),
            ("13:35", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
        ],
    },
    {
        "route_id": WEEKDAY_ROUTE_ID,
        "service_id": WEEKDAY_SERVICE_ID,
        "trip_id": "WEEKEB",
        "shape_id": "WEEKEB",
        "direction_id": DirectionId.OUTBOUND.value,
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("07:10", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
            ("07:40", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
        ],
    },
    {
        "route_id": WEEKDAY_ROUTE_ID,
        "service_id": WEEKDAY_SERVICE_ID,
        "trip_id": "WEEKWB",
        "shape_id": "WEEKWB",
        "direction_id": DirectionId.INBOUND.value,
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("16:00", "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b"),
            ("16:30", "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0"),
        ],
    },
    {
        "route_id": LUBEC_ROUTE_ID,
        "service_id": FW_OF_MONTH_SERVICE_ID,
        "trip_id": "LBCWB",
        "shape_id": "LBCWB",
        "direction_id": DirectionId.INBOUND.value,
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("8:45", "STOP-421bb314-1894-4c15-bb6f-0fec17fcb7d9"),
            ("9:30", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
        ],
    },
    {
        "route_id": LUBEC_ROUTE_ID,
        "service_id": FW_OF_MONTH_SERVICE_ID,
        "trip_id": "LBCEB",
        "shape_id": "LBCEB",
        "direction_id": DirectionId.OUTBOUND.value,
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("11:30", "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10"),
            ("12:15", "STOP-421bb314-1894-4c15-bb6f-0fec17fcb7d9"),
        ],
    },
    {
        "route_id": SCHOOL_ROUTE_ID,
        "service_id": SCHOOL_SERVICE_ID,
        "trip_id": "SCHLSB",
        "shape_id": "SCHLSB",
        "direction_id": DirectionId.OUTBOUND.value,
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("8:40", "STOP-1332dd93-e6a0-45e1-b4fd-940d57659703"),
            ("9:05", "STOP-1c531172-cfcf-4843-8de5-ca23289d30b5"),
        ],
    },
    {
        "route_id": SCHOOL_ROUTE_ID,
        "service_id": SCHOOL_SERVICE_ID,
        "trip_id": "SCHLNB",
        "shape_id": "SCHLNB",
        "direction_id": DirectionId.INBOUND.value,
        "bikes_allowed": BikesAllowed.YES.value,
        "stop_times": [
            ("13:35", "STOP-1c531172-cfcf-4843-8de5-ca23289d30b5"),
            ("14:00", "STOP-1332dd93-e6a0-45e1-b4fd-940d57659703"),
        ],
    },
]

STOPS = [
    # WCC
    {
        "stop_id": "STOP-9034671c-e991-4439-9e71-a05a8599a56f",
        "stop_name": "Calais",
        "stop_desc": "Marden's Parking Lot",
        "stop_lat": 45.18854669392266,
        "stop_lon": -67.28220840306957,
    },
    {
        "stop_id": "STOP-14ed8aff-0f08-4ac4-89fe-e9b172db07bb",
        "stop_name": "Perry",
        "stop_desc": "Wabanaki Mall",
        "stop_lat": 44.97231404736198,
        "stop_lon": -67.07493005575536,
    },
    {
        "stop_id": "STOP-2ad237c0-4dfe-4a50-a8cd-cec8972e1922",
        "stop_name": "Pembroke",
        "stop_desc": "Corner of Rt. 214 & Rt. 1",
        "stop_lat": 44.94965682737453,
        "stop_lon": -67.17849654043128,
    },
    {
        "stop_id": "STOP-c48d97aa-f7b1-4560-b697-048d4aca8f74",
        "stop_name": "Dennysville",
        "stop_desc": "Cobscook Bay Cafe",
        "stop_lat": 44.90308868913789,
        "stop_lon": -67.22050781904481,
    },
    {
        "stop_id": "STOP-d530cc40-12bd-4071-95de-52fbaf1d7d23",
        "stop_name": "Whiting",
        "stop_desc": "Community Center/Store",
        "stop_lat": 44.791233559261826,
        "stop_lon": -67.17424929425094,
    },
    {
        "stop_id": "STOP-477b3ace-4389-47e8-a4c7-cb32cd874a10",
        "stop_name": "Machias",
        "stop_desc": "Irving Mainway",
        "stop_lat": 44.71747416614576,
        "stop_lon": -67.45320159645519,
    },
    {
        "stop_id": "STOP-3186da65-c835-47ae-9095-f3881148ffc9",
        "stop_name": "Jonesboro",
        "stop_desc": "Swamp Yankee BBQ",
        "stop_lat": 44.662060972756706,
        "stop_lon": -67.57294144907351,
    },
    {
        "stop_id": "STOP-be554e9d-f180-450f-902b-a772328ac4dd",
        "stop_name": "Columbia",
        "stop_desc": "Elmer's Discount",
        "stop_lat": 44.64287175736857,
        "stop_lon": -67.76299771361364,
    },
    {
        "stop_id": "STOP-7a5a3410-4d73-4cbf-aea1-df3d4aa243f2",
        "stop_name": "Milbridge",
        "stop_desc": "44 North Rest.",
        "stop_lat": 44.537812397946055,
        "stop_lon": -67.88149880431949,
    },
    {
        "stop_id": "STOP-e354cfda-7054-4ed6-b5c4-e7a4975cfdbd",
        "stop_name": "Gouldsboro",
        "stop_desc": "Young's Market",
        "stop_lat": 44.484226237813715,
        "stop_lon": -68.1149969959795,
    },
    {
        "stop_id": "STOP-970a9e30-06d7-4ddb-98cc-49cdee5588cb",
        "stop_name": "Sullivan",
        "stop_desc": "Sullivan REC. Center",
        "stop_lat": 44.53024290489276,
        "stop_lon": -68.22476574771778,
    },
    {
        "stop_id": "STOP-fc0ebfb0-a667-4382-88d3-d3f194bf26b6",
        "stop_name": "Hancock",
        "stop_desc": "Village Store",
        "stop_lat": 44.53014123436881,
        "stop_lon": -68.25858959486574,
    },
    {
        "stop_id": "STOP-2cd4673a-e3d0-472f-9654-37a6c9233e4a",
        "stop_name": "Ellsworth",
        "stop_desc": "Main Entrance Mill Mall, Out Back",
        "stop_lat": 44.551403972284845,
        "stop_lon": -68.43000587506339,
    },
    {
        "stop_id": "STOP-3012643a-132d-4c0d-974e-cdc8714f9368",
        "stop_name": "Bangor (Concord Trailways)",
        "stop_desc": "Concord Trailways",
        "stop_lat": 44.816594110637595,
        "stop_lon": -68.80876371853913,
    },
    {
        "stop_id": "STOP-8f56e854-d898-49f8-aef1-f6420a0c6042",
        "stop_name": "Bangor (Airport)",
        "stop_desc": "Bangor Airport",
        "stop_lat": 44.80905167866493,
        "stop_lon": -68.81786055142301,
    },
    # ELLS
    {
        "stop_desc": "Post Office",
        "stop_id": "STOP-b11bb36f-65f5-4bfe-abb8-bdf1d76ac3b9",
        "stop_lat": 44.51930662452464,
        "stop_lon": -67.61194499329405,
        "stop_name": "Beals Island",
    },
    {
        "stop_desc": "Post Office",
        "stop_id": "STOP-cce489d3-8d6c-4e48-813d-c2d1d2acb90b",
        "stop_lat": 44.531579513613664,
        "stop_lon": -67.60136565981361,
        "stop_name": "Jonesport",
    },
    {
        "stop_desc": "Town Office",
        "stop_id": "STOP-709e5965-7b27-4c47-a1de-1eedbea4350e",
        "stop_lat": 44.65327843995525,
        "stop_lon": -67.72815087072122,
        "stop_name": "Addison",
    },
    {
        "stop_desc": "Pleasant View Appartments",
        "stop_id": "STOP-fc77e641-ea79-4e44-b050-16cf14331355",
        "stop_lat": 44.6358184790437,
        "stop_lon": -67.73386558458837,
        "stop_name": "Columbia Falls",
    },
    {
        "stop_desc": "4 Corners",
        "stop_id": "STOP-a8fb5add-97f2-4284-8533-1f2181fdc6f8",
        "stop_lat": 44.64318156877917,
        "stop_lon": -67.76194701794302,
        "stop_name": "Columbia",
    },
    {
        "stop_desc": "Housing Appartments",
        "stop_id": "STOP-a64ef87a-091d-47ea-9c17-8f1652e1d882",
        "stop_lat": 44.6201213065024,
        "stop_lon": -67.80826855268631,
        "stop_name": "Harrington",
    },
    {
        "stop_desc": "Narraguagus Estates",
        "stop_id": "STOP-fc06a983-3770-4ca9-882e-4b90cd0c3573",
        "stop_lat": 44.59677148932213,
        "stop_lon": -67.93183540873198,
        "stop_name": "Cherryfield",
    },
    {
        "stop_desc": "West Manor",
        "stop_id": "STOP-d6a9c3c6-72f3-47fb-9317-bd223cbd3764",
        "stop_lat": 44.53754398311699,
        "stop_lon": -67.87995630656948,
        "stop_name": "Milbridge",
    },
    {
        "stop_desc": "Town Office",
        "stop_id": "STOP-e3f84be2-a7a6-43f9-8489-76cefb81d9c0",
        "stop_lat": 44.513255761192,
        "stop_lon": -67.96625333615914,
        "stop_name": "Steuben",
    },
    {
        "stop_desc": "Town",
        "stop_id": "STOP-14ae1c74-7f7c-4204-be30-265e030a1c35",
        "stop_lat": 44.54300199772945,
        "stop_lon": -68.42019965314486,
        "stop_name": "Ellsworth",
    },
    # Lubec
    {
        "stop_desc": "Town",
        "stop_id": "STOP-421bb314-1894-4c15-bb6f-0fec17fcb7d9",
        "stop_lat": 44.85869201099502,
        "stop_lon": -66.98336351926885,
        "stop_name": "Lubec",
    },
    # School Route
    {
        "stop_desc": "Franklin Trading Post",
        "stop_id": "STOP-1332dd93-e6a0-45e1-b4fd-940d57659703",
        "stop_lat": 44.58890243818803,
        "stop_lon": -68.22318410664123,
        "stop_name": "Franklin",
    },
    {
        "stop_desc": "Winter Harbor Garage",
        "stop_id": "STOP-1c531172-cfcf-4843-8de5-ca23289d30b5",
        "stop_lat": 44.394562204134324,
        "stop_lon": -68.0851666416681,
        "stop_name": "Winter Harbor",
    },
]

# Generate stops.geojson
fc = geojson.FeatureCollection([
    geojson.Feature(
        geometry=geojson.Point((s["stop_lon"], s["stop_lat"])),
        properties={
            "stop_id": s["stop_id"],
            "stop_name": s["stop_name"],
            "stop_desc": s["stop_desc"],
        },
    )
    for s in STOPS
])
with open(f"{script_dir}/stops.geojson", "w") as f:
    geojson.dump(fc, f, sort_keys=True, indent=2)

# Generate route URLs
stop_lookup = {s["stop_id"]: (s["stop_lon"], s["stop_lat"]) for s in STOPS}

# 2) Generate URLs for each trip
base = "https://brouter.de/brouter-web/#map=11/44.5866/-68.0370/standard&lonlats="
suffix = "&profile=car-fast"

urls = {
    trip["trip_id"]: (
        base
        + ";".join(
            ",".join(map(str, stop_lookup[stop_id]))
            for _, stop_id in trip["stop_times"]
        )
        + suffix
    )
    for trip in TRIPS
}
print(json.dumps(urls, indent=2))

CALENDAR = [
    {
        "service_id": DAILY_SERVICE_ID,
        "monday": ServiceAvailable.YES.value,
        "tuesday": ServiceAvailable.YES.value,
        "wednesday": ServiceAvailable.YES.value,
        "thursday": ServiceAvailable.YES.value,
        "friday": ServiceAvailable.YES.value,
        "saturday": ServiceAvailable.YES.value,
        "sunday": ServiceAvailable.YES.value,
        "start_date": FEED_START,
        "end_date": FEED_END,
    },
    {
        "service_id": WEEKDAY_SERVICE_ID,
        "monday": ServiceAvailable.YES.value,
        "tuesday": ServiceAvailable.YES.value,
        "wednesday": ServiceAvailable.YES.value,
        "thursday": ServiceAvailable.YES.value,
        "friday": ServiceAvailable.YES.value,
        "saturday": ServiceAvailable.NO.value,
        "sunday": ServiceAvailable.NO.value,
        "start_date": FEED_START,
        "end_date": FEED_END,
    },
    {
        "service_id": SCHOOL_SERVICE_ID,
        "monday": ServiceAvailable.YES.value,
        "tuesday": ServiceAvailable.YES.value,
        "wednesday": ServiceAvailable.YES.value,
        "thursday": ServiceAvailable.YES.value,
        "friday": ServiceAvailable.YES.value,
        "saturday": ServiceAvailable.NO.value,
        "sunday": ServiceAvailable.NO.value,
        "start_date": 20250902,
        "end_date": 20260515,  # https://machias.edu/registrar/wp-content/uploads/sites/93/2024/08/2025-2026-Academic-Calendar.pdf
    },
    {
        "service_id": MONDAY_SERVICE_ID,
        "monday": ServiceAvailable.YES.value,
        "tuesday": ServiceAvailable.NO.value,
        "wednesday": ServiceAvailable.NO.value,
        "thursday": ServiceAvailable.NO.value,
        "friday": ServiceAvailable.NO.value,
        "saturday": ServiceAvailable.NO.value,
        "sunday": ServiceAvailable.NO.value,
        "start_date": FEED_START,
        "end_date": FEED_END,
    },
    {
        "service_id": TUESDAY_SERVICE_ID,
        "monday": ServiceAvailable.NO.value,
        "tuesday": ServiceAvailable.YES.value,
        "wednesday": ServiceAvailable.NO.value,
        "thursday": ServiceAvailable.NO.value,
        "friday": ServiceAvailable.NO.value,
        "saturday": ServiceAvailable.NO.value,
        "sunday": ServiceAvailable.NO.value,
        "start_date": FEED_START,
        "end_date": FEED_END,
    },
]

CALENDAR_DATES = [
    [
        {
            "service_id": FW_OF_MONTH_SERVICE_ID,
            "date": int(f"{year:4}{month:02}{day:02}"),
            "exception_type": ServiceException.ADDED.value,
        }
        # Look at the first week and choose the first wednesday
        for day in range(1, 8)
        if datetime(year=year, month=month, day=day).weekday()
        == calendar.WEDNESDAY.value
    ].pop()
    # Look at each month for the next 2 years
    for year, month in [
        (now.year + (now.month - 1 + i) // 12, (now.month - 1 + i) % 12 + 1)
        for i in range(12 * 2)
    ]
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
    "calendar_dates.txt": CALENDAR_DATES,
    "feed_info.txt": [FEED_INFO],
    "shapes.txt": [
        {
            "shape_id": trip["shape_id"],
            "shape_pt_lat": lat,
            "shape_pt_lon": lon,
            "shape_pt_sequence": seq,
        }
        for trip in TRIPS
        if "shape_id" in trip
        for seq, (lon, lat, *_) in enumerate(
            _coords(f"{script_dir}/shapes/{trip['shape_id']}.geojson"), start=1
        )
    ],
}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdirname:
        for filename, data in FILES.items():
            pd.DataFrame(data).to_csv(Path(tmpdirname) / filename, index=False)
        shutil.make_archive(str(feed_path), "zip", tmpdirname)
