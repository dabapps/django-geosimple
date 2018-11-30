django-geosimple [![travis][travis-image]][travis-url] [![pypi][pypi-image]][pypi-url]
===================================
> Basic geospatial helpers for Django

### Supports

 - Python 2.7, 3.4, 3.5
 - Django 1.6 up to 1.10


GeoDjango is an incredibly powerful set of extensions to Django for handling complex geospatial data. However, it has a long list of prerequisites (a spatial database such as PostgreSQL with PostGIS, GEOS, a specialised database backend, etc). For many projects that have only basic geospatial requirements, the overhead of getting GeoDjango up and running is painful.

*Note: if you are building an application with complex or high-performance geospatial requirements, please consider using GeoDjango.*

django-geosimple provides the following:

* a custom model field type for storing locations as geohashes.
* a way of querying locations by *approximate* distance from a point, based on on geohash expansion and prefix string search.
* a set of methods for filtering and sorting query results *in memory*, which are (obviously) only suitable for relatively small sets of locations.

It works on any database backend supported by Django with no modifications. It is based on the `geopy` and `python-geohash` libraries.

*This is an experimental project - any use is at your own risk!

Background
----------

Conceptually, the sorts of geospatial calculations that *most* web applications need to perform are relatively straightforward:

*Find all points within a given distance from a starting point, and/or sort the points by distance.*

The `geopy` library provides an easy, fast method for calculating the distance between two points. If we calculate this distance for every point in our database, we can easily sort them and discard any that fall outside a given radius.

Although computers are fast (my laptop can calculate and sort distances for 20,000 points in less than a second), this approach clearly doesn't scale very well. It uses lots of memory, and with a large-ish number of points the calculations take too much time to be performed in a web request/response cycle.

[Geohash](https://en.wikipedia.org/wiki/Geohash) is a fairly well-established way of representing geographical locations as human-readable strings that have a desirable property: they get *gradually less accurate* as you discard characters from the end of the code. It's also easy to calculate the neighbours of a given geohash.

By storing our geographical points as geohashes, we can "jump start" the sorting/filtering algorithm by crudely filtering the points to those which lie *approximately* in the area we're interested in. This makes a brute-force in-memory sorting algorithm much more usable, especially with relatively small numbers of locations.

GeohashField
------------

A `GeohashField` provides a simple way to store a location as a Geohash. Internally, the location is stored as a 12-character `CharField`. The value of the field can be set in a few ways:

* Directly as a string, if you already know the geohash
* As a (latitude, longitude) two-tuple
* From a dictionary with `latitude` and `longitude` (or `lat` and `lon`) keys
* From an object with `latitude` and `longitude` (or `lat` and `lon` properties)

```python
class CoffeeShop(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    location = geosimple.GeohashField()

marwood = CoffeeShop(name="The Marwood", website="http://themarwood.com/")

marwood.location = (50.822482, -0.141449)

# or..
marwood.location = {'latitude': 50.822482, 'longitude': -0.141449}

# or
marwood.location = geopy.Point(50.822482, -0.141449)

marwood.save()
```

You can retrieve the location in corresponding formats, too:

```pycon
>>> marwood = CoffeeShop.objects.get(name="The Marwood")
>>> print marwood.location
'gcpchgbyrvrf'
>>> print marwood.location.as_tuple()
(50.82248208113015, -0.14144914224743843)
>>> print marwood.location.as_dict()
{'latitude': 50.82248208113015, 'longitude': -0.14144914224743843}
>>> print marwood.location.latitude
50.82248208113015
>>> print marwood.location.longitude
-0.14144914224743843
```

Geospatial queries
------------------

Attach a `geosimple.GeoManager` to your model to provide geospatial filtering and sorting.

### Geohash expansion search

You can perform a fairly crude filter of your locations by searching nearby geohashes, using the `approx_distance_lt` lookup:

```pycon
>>> dabapps_office = (50.8229, -0.143219)
>>> distance = 0.5  # kilometres
>>> CoffeeShop.objects.filter(location__approx_distance_lt=(dabapps_office, distance))
```

The value is a two-tuple of a location and a distance. The location can be specified in any of the ways supported by field assignment above (two-tuple, dictionary, object, etc). The distance can either be a number in kilometers, or a `geopy.distance.Distance` instance (aliased to `geosimple.Distance` for convenience), which can be used to represent all manner of other distance measurements.

This works by creating a set of nine geohashes that cover the area described by your radius. Depending on the distance you requested, this area might be significantly bigger than the distance you asked for, so some of your results will almost certainly be incorrect!

### In-memory distance filtering

After a crude filter has been performed, `django-geosimple` can post-process your query results to discard any that don't fit with in the radius you requested. This is done *in-memory*, so is only sensible to use with relatively small sets of results. The crude geohash search described above is performed to chop down your result set to a sensible size first.

```pycon
>>> CoffeeShop.objects.filter(location__distance_lt=(dabapps_office, distance))
```

You don't need to use both `__approx_distance_lt` and `__distance_lt`: using the latter implies the former.

### In-memory distance sorting

You can order a set of results by distance from a point. Again, this is done *in-memory* when the queryset is iterated, so don't try to use it for large result sets.

```pycon
>>> CoffeeShop.objects.order_by_distance_from(dabapps_office)
```

If you've already filtered the points by distance, you don't need to supply the location again:

```
>>> CoffeeShop.objects.filter(location__distance_lt=(dabapps_office, Distance(miles=1))).order_by_distance()
```

### Distance annotation

If either of the in-memory filtering or sorting methods are used, each item in the queryset will be annotated with the distance from the given point. The property used is the name of the field with `_distance` appended. So, in the example above, the property will be named `location_distance`. This will be a `geopy.Distance` instance. You can force these annotations to be added by calling `with_distance_annotations`, passing a location.


[travis-image]: https://travis-ci.org/dabapps/django-geosimple.svg?branch=master
[travis-url]: https://travis-ci.org/dabapps/django-geosimple

[pypi-image]: https://badge.fury.io/py/django-geosimple.svg
[pypi-url]: https://pypi.python.org/pypi/django-geosimple/

## Code of conduct

For guidelines regarding the code of conduct when contributing to this repository please review [https://www.dabapps.com/open-source/code-of-conduct/](https://www.dabapps.com/open-source/code-of-conduct/)
