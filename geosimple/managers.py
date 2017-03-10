from copy import copy, deepcopy
from django.db import models
from geosimple.utils import geohash_length_for_error, convert_to_point
from geopy.distance import Distance


APPROX_DISTANCE_POSTFIX = "__approx_distance_lt"
EXACT_DISTANCE_POSTFIX = "__distance_lt"


class GeoQuerySet(models.query.QuerySet):

    def __init__(self, *args, **kwargs):
        super(GeoQuerySet, self).__init__(*args, **kwargs)
        self._postprocess = {}

    def _clone(self, **kwargs):
        c = super(GeoQuerySet, self)._clone(**kwargs)
        c._postprocess = copy(self._postprocess)
        return c

    def filter(self, *args, **kwargs):
        """Override filter to support custom lookups"""

        filters = None
        for key in deepcopy(kwargs).keys():
            if not key.endswith((APPROX_DISTANCE_POSTFIX, EXACT_DISTANCE_POSTFIX)):
                continue

            location, radius = kwargs.pop(key)
            radius = Distance(radius)
            is_exact = key.endswith(EXACT_DISTANCE_POSTFIX)
            field_name = key.replace(APPROX_DISTANCE_POSTFIX, '').replace(EXACT_DISTANCE_POSTFIX, '')
            filters = self._create_approx_distance_filter(field_name, location, radius)

            if is_exact:
                self._postprocess['field_name'] = field_name
                self._postprocess['location'] = location
                self._postprocess['radius'] = radius

        result = super(GeoQuerySet, self).filter(*args, **kwargs)

        if filters:
            return result.filter(filters)
        return result

    def _create_approx_distance_filter(self, field_name, location, radius):
        geohash_length = geohash_length_for_error(radius.kilometers)
        geohash = convert_to_point(location).geohash.trim(geohash_length)
        expanded = geohash.expand()
        filters = models.Q()
        for item in expanded:
            filters.add(models.Q(**{"%s__startswith" % field_name: item}), models.Q.OR)
        return filters

    def order_by_distance(self):
        self._postprocess['sort'] = True
        return self._clone()

    def iterator(self):
        result_iter = super(GeoQuerySet, self).iterator()

        if not self._postprocess:
            return result_iter

        field_name = self._postprocess['field_name']
        location = self._postprocess['location']
        radius = self._postprocess['radius']

        distance_property_name = "%s_distance" % field_name

        results = []
        for result in list(result_iter):
            result_location = getattr(result, field_name)
            distance_from_location = result_location.point.distance_from(convert_to_point(location))
            setattr(result, distance_property_name, distance_from_location)
            if distance_from_location.km < radius.km:
                results.append(result)

        if self._postprocess.get('sort'):
            return iter(sorted(results, key=lambda item: getattr(item, distance_property_name).km))
        return iter(results)

    def count(self):
        if self._postprocess:
            return len(list(self.iterator()))
        else:
            return super(GeoQuerySet, self).count()

    def __getitem__(self, k):
        if self._postprocess:
            return list(self.iterator()).__getitem__(k)
        else:
            return super(GeoQuerySet, self).__getitem__(k)


class GeoManager(models.Manager):

    def get_query_set(self):
        return GeoQuerySet(self.model)

    def get_queryset(self):
        return self.get_query_set()
