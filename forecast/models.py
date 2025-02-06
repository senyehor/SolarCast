from django.db import models

from locations.models import Location


class LocationModel(models.Model):
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='model')
    filename = models.CharField(null=False)
    created_at = models.DateTimeField(auto_now=True)

