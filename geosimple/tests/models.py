from django.db import models
from geosimple import GeohashField, GeoManager


class CoffeeShop(models.Model):

    name = models.CharField(max_length=100)
    location = GeohashField()

    objects = GeoManager()

    def __unicode__(self):
        return self.name
