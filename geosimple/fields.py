from django.db import models


class GeohashField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12
        return super(GeohashField, self).__init__(*args, **kwargs)
