from django.db import models
from geosimple.utils import convert_to_point


class GeohashField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12
        return super(GeohashField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if not isinstance(value, str):
            value = convert_to_point(value).geohash
        return super(GeohashField, self).get_prep_value(value)
