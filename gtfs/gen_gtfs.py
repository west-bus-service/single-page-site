from enum import Enum


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
        "service_id": "",  # TODO: ref calendar.service_id
        "trip_id": "WCCWB",
        "trip_short_name": "Bangor (via Rt 1)",
        "direction_id": DirectionId.INBOUND,
        "shape_id": "",  # TODO: shapes.shape_id
        "bikes_allowed": BikesAllowed.YES,
    },
]
