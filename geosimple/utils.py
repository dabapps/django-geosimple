import geohash


class Point(object):

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    @property
    def geohash(self):
        return Geohash(geohash.encode(self.latitude, self.longitude))


class Geohash(str):

    _point = None

    @property
    def point(self):
        if not self._point:
            self._point = convert_to_point(geohash.decode(self))
        return self._point


def convert_to_point(arg):
    """Flexibly convert a range of different types to a Point"""

    # Support objects with "latitude" and "longitude" properties
    try:
        return Point(arg.latitude, arg.longitude)
    except AttributeError:
        pass

    # Support objects with "lat" and "lon" properties
    try:
        return Point(arg.lat, arg.lon)
    except AttributeError:
        pass

    # Support dicts with "latitude" and "longitude" keys
    try:
        return Point(arg["latitude"], arg["longitude"])
    except (KeyError, TypeError):
        pass

    # Support dicts with "lat" and "lon" keys
    try:
        return Point(arg["lat"], arg["lon"])
    except (KeyError, TypeError):
        pass

    # Support (lat, lon) two-tuple
    try:
        lat, lon = arg
        return Point(lat, lon)
    except TypeError:
        pass
