from django.db import models
from geosimple.utils import Geohash, convert_to_point


class GeohashField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12
        kwargs['db_index'] = True
        return super(GeohashField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, basestring):
            return Geohash(value)
        return convert_to_point(value).geohash


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^geosimple\.fields\.GeohashField"])
except:
    pass
