from django.db import models
from geosimple.utils import Geohash, convert_to_point


class GeohashField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12
        return super(GeohashField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, basestring):
            return Geohash(value)
        return convert_to_point(value).geohash
