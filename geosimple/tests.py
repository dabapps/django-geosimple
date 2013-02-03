from django.test import TestCase
from geosimple.utils import convert_to_point


class PointConversionTestCase(TestCase):

    LAT = 50.822482
    LON = -0.141449

    def test_tuple(self):
        point = convert_to_point((self.LAT, self.LON))
        self.assertEqual(point.latitude, self.LAT)
        self.assertEqual(point.longitude, self.LON)

    def test_object_with_verbose_properties(self):

        class Dummy(object):
            pass

        location = Dummy()
        location.latitude = self.LAT
        location.longitude = self.LON
        point = convert_to_point(location)
        self.assertEqual(point.latitude, self.LAT)
        self.assertEqual(point.longitude, self.LON)

    def test_object_with_short_properties(self):

        class Dummy(object):
            pass

        location = Dummy()
        location.lat = self.LAT
        location.lon = self.LON
        point = convert_to_point(location)
        self.assertEqual(point.latitude, self.LAT)
        self.assertEqual(point.longitude, self.LON)

    def test_dict_with_verbose_keys(self):
        location = {'latitude': self.LAT, 'longitude': self.LON}
        point = convert_to_point(location)
        self.assertEqual(point.latitude, self.LAT)
        self.assertEqual(point.longitude, self.LON)

    def test_dict_with_short_keys(self):
        location = {'lat': self.LAT, 'lon': self.LON}
        point = convert_to_point(location)
        self.assertEqual(point.latitude, self.LAT)
        self.assertEqual(point.longitude, self.LON)
