from django.db import models
from geosimple.utils import geohash_length_for_error, convert_to_point
from geopy.distance import Distance


APPROX_DISTANCE_POSTFIX = "__approx_distance_lt"


class GeoQuerySet(models.query.QuerySet):

    def filter(self, *args, **kwargs):
        """Override filter to support custom lookups"""
        approx_distance_filters = [filter for filter in kwargs.keys() if filter.endswith(APPROX_DISTANCE_POSTFIX)]

        filters = []
        for filter in approx_distance_filters:
            location, distance = kwargs.pop(filter)
            field_name = filter.replace(APPROX_DISTANCE_POSTFIX, '')
            filters.append(self._create_approx_distance_filter(field_name, location, distance))

        result = super(GeoQuerySet, self).filter(*args, **kwargs)

        if filters:
            return result.filter(*filters)
        return result

    def _create_approx_distance_filter(self, field_name, location, distance):
        distance = Distance(distance)
        geohash_length = geohash_length_for_error(distance.kilometers)
        geohash = convert_to_point(location).geohash.trim(geohash_length)
        expanded = geohash.expand()
        filters = models.Q()
        for item in expanded:
            filters.add(models.Q(**{"%s__startswith" % field_name: item}), models.Q.OR)
        return filters


class GeoManager(models.Manager):

    def get_query_set(self):
        return GeoQuerySet(self.model)
