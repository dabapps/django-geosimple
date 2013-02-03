from django.db import models
from geosimple import GeohashField


class CoffeeShop(models.Model):

    name = models.CharField(max_length=100)
    location = GeohashField()
