from django.test import TestCase
from geosimple.utils import Point, Geohash, convert_to_point
from geosimple.tests.models import CoffeeShop

# Example lat/lon pair and corresponding geohash
LAT = 50.822482
LON = -0.141449
GEOHASH = 'gcpchgbyrvrf'


class PointConversionTestCase(TestCase):

    def test_tuple(self):
        point = convert_to_point((LAT, LON))
        self.assertEqual(point.latitude, LAT)
        self.assertEqual(point.longitude, LON)

    def test_object_with_verbose_properties(self):

        class Dummy(object):
            pass

        location = Dummy()
        location.latitude = LAT
        location.longitude = LON
        point = convert_to_point(location)
        self.assertEqual(point.latitude, LAT)
        self.assertEqual(point.longitude, LON)

    def test_object_with_short_properties(self):

        class Dummy(object):
            pass

        location = Dummy()
        location.lat = LAT
        location.lon = LON
        point = convert_to_point(location)
        self.assertEqual(point.latitude, LAT)
        self.assertEqual(point.longitude, LON)

    def test_dict_with_verbose_keys(self):
        location = {'latitude': LAT, 'longitude': LON}
        point = convert_to_point(location)
        self.assertEqual(point.latitude, LAT)
        self.assertEqual(point.longitude, LON)

    def test_dict_with_short_keys(self):
        location = {'lat': LAT, 'lon': LON}
        point = convert_to_point(location)
        self.assertEqual(point.latitude, LAT)
        self.assertEqual(point.longitude, LON)


class PointGeohashTestCase(TestCase):

    def test_convert_point_to_geohash(self):
        point = Point(LAT, LON)
        self.assertEqual(point.geohash, GEOHASH)

    def test_convert_geohash_to_point(self):
        point = Point(LAT, LON)
        geohash = point.geohash
        self.assertAlmostEqual(geohash.point.latitude, LAT, places=5)
        self.assertAlmostEqual(geohash.point.longitude, LON, places=5)


class GeohashFieldTestCase(TestCase):

    def setUp(self):
        self.shop = CoffeeShop(name='The Marwood')

    def get_shop(self):
        return CoffeeShop.objects.get()

    def test_basic_string_behaviour(self):
        self.shop.location = GEOHASH
        self.shop.save()

        shop = self.get_shop()
        self.assertEqual(shop.location, GEOHASH)

    def test_type_conversion_to_database(self):
        self.shop.location = (LAT, LON)
        self.shop.save()

        shop = self.get_shop()
        self.assertIsInstance(shop.location, Geohash)
        self.assertEqual(shop.location, GEOHASH)

    def test_type_conversion_from_database(self):
        self.shop.location = (LAT, LON)
        self.shop.save()

        shop = self.get_shop()
        geohash = shop.location
        self.assertAlmostEqual(geohash.point.latitude, LAT, places=5)
        self.assertAlmostEqual(geohash.point.longitude, LON, places=5)
