from typing import Any, Iterable, List, Optional

from ipyleaflet import Map, Marker, Polygon, Polyline
from ipywidgets import HTML
from shapely.geometry import LineString

from ..core import Airspace, Flight, FlightPlan
from ..core.mixins import PointMixin


def flight_leaflet(flight: "Flight", **kwargs) -> Optional[Polyline]:
    """Returns a Leaflet layer to be directly added to a Map.

    .. warning::
        This is only available if the Leaflet `plugin <plugins.html>`_ is
        activated. (true by default)

    The elements passed as kwargs as passed as is to the PolyLine constructor.

    Example usage:

    >>> from ipyleaflet import Map
    >>> # Center the map near the landing airport
    >>> m = Map(center=flight.at().latlon, zoom=7)
    >>> m.add_layer(flight)  # this works as well with default options
    >>> m.add_layer(flight.leaflet(color='red'))
    >>> m
    """
    shape = flight.shape
    if shape is None:
        return None

    kwargs = {**dict(fill_opacity=0, weight=3), **kwargs}
    return Polyline(
        locations=list((lat, lon) for (lon, lat, _) in shape.coords), **kwargs
    )


def flightplan_leaflet(
    flightplan: "FlightPlan", **kwargs
) -> Optional[Polyline]:
    """Returns a Leaflet layer to be directly added to a Map.

    .. warning::
        This is only available if the Leaflet `plugin <plugins.html>`_ is
        activated. (true by default)

    The elements passed as kwargs as passed as is to the PolyLine constructor.
    """

    shape = flightplan.shape
    if shape is None:
        return None

    coords: Iterable = list()
    if isinstance(shape, LineString):
        coords = list((lat, lon) for (lon, lat, *_) in shape.coords)
    else:
        # In case a FlightPlan could not resolve all parts
        coords = list(
            list((lat, lon) for (lon, lat, *_) in s.coords) for s in shape
        )

    kwargs = {**dict(fill_opacity=0, weight=3), **kwargs}
    return Polyline(locations=coords, **kwargs)


def airspace_leaflet(airspace: "Airspace", **kwargs) -> Polygon:
    """Returns a Leaflet layer to be directly added to a Map.

    .. warning::
        This is only available if the Leaflet `plugin <plugins.html>`_ is
        activated. (true by default)

    The elements passed as kwargs as passed as is to the Polygon constructor.
    """
    shape = airspace.flatten()

    kwargs = {**dict(weight=3), **kwargs}
    coords: List[Any] = []
    if shape.geom_type == "Polygon":
        coords = list((lat, lon) for (lon, lat, *_) in shape.exterior.coords)
    else:
        coords = list(
            list((lat, lon) for (lon, lat, *_) in piece.exterior.coords)
            for piece in shape
        )

    return Polygon(locations=coords, **kwargs)


def point_leaflet(point: "PointMixin", **kwargs) -> Marker:
    """Returns a Leaflet layer to be directly added to a Map.

    .. warning::
        This is only available if the Leaflet `plugin <plugins.html>`_ is
        activated. (true by default)

    The elements passed as kwargs as passed as is to the Marker constructor.
    """

    default = dict()
    if hasattr(point, "name"):
        default["title"] = point.name

    kwargs = {**default, **kwargs}
    marker = Marker(location=(point.latitude, point.longitude), **kwargs)

    label = HTML()
    label.value = repr(point)
    marker.popup = label

    return marker


_old_add_layer = Map.add_layer


def map_add_layer(_map, elt, **kwargs):
    if any(
        isinstance(elt, c) for c in (Flight, FlightPlan, Airspace, PointMixin)
    ):
        layer = elt.leaflet(**kwargs)
        _old_add_layer(_map, layer)
        return layer
    return _old_add_layer(_map, elt)


def _onload():
    setattr(Flight, "leaflet", flight_leaflet)
    setattr(FlightPlan, "leaflet", flightplan_leaflet)
    setattr(Airspace, "leaflet", airspace_leaflet)
    setattr(PointMixin, "leaflet", point_leaflet)
    setattr(Map, "add_layer", map_add_layer)
