from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=255, verbose_name="Location Name")
    longitude = models.FloatField(verbose_name="Longitude")
    latitude = models.FloatField(verbose_name="Latitude")
    notes = models.TextField(blank=True, null=True, verbose_name="Additional Notes")

    def __str__(self):
        return self.name


class SolarGenerationData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="generation_data")
    interval_start = models.DateTimeField()
    generated_energy = models.FloatField(help_text="Energy generated in kWh")

    class Meta:
        verbose_name = "Solar Generation Data"
        verbose_name_plural = "Solar Generation Data"
        ordering = ["interval_start"]

    def __str__(self):
        return f"{self.location.name} - {self.interval_start} - {self.generated_energy} kWh"


class WeatherData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_data')
    time = models.DateTimeField()
    temperature = models.FloatField()
    relative_humidity = models.IntegerField()
    cloud_coverage = models.IntegerField()
    radiation_w_m2 = models.IntegerField()

