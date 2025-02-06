import csv
from datetime import datetime

import pytz
from django.contrib import messages
from django.db.transaction import atomic
from django.shortcuts import redirect, render

from forecast.forms import CSVUploadForm
from locations.models import Location, SolarGenerationData
from .models import WeatherData
from .utils import fetch_weather_data


# Create your views here.
def upload_generation_data(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            try:
                with atomic():
                    decoded_file = csv_file.read().decode("utf-8")
                    reader = csv.reader(decoded_file.splitlines())
                    next(reader)  # Skip the header row
                    for row in reader:
                        interval_start = row[0]
                        generated_energy = row[1]
                        location_id = row[2]
                        location = Location.objects.filter(id=location_id).first()
                        if not location:
                            messages.error(request, f"Об'єкт ID {location_id} не існує.")
                            raise Exception
                        SolarGenerationData.objects.create(
                            location_id=location.id,
                            interval_start=interval_start,
                            generated_energy=generated_energy
                        )
                messages.success(request, "Дані успішно завантажено")
            except Exception as e:
                messages.error(request, f"При опрацюванні файлі сталася помилка")
                raise e
            return redirect('forecast_main')
    else:
        form = CSVUploadForm()
    return render(request, "upload_generation_data.html", {"form": form})


def fetch_weather_view(request):
    if request.method == 'POST':
        location_id = request.POST.get('location')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            messages.error(request, "Такої локації не існує")
            return redirect('fetch_weather')

        data = fetch_weather_data(location.latitude, location.longitude, start_date, end_date)
        with atomic():
            if data and "hourly" in data:
                hourly_data = data["hourly"]
                times = hourly_data["time"]
                temperatures = hourly_data["temperature_2m"]
                humidities = hourly_data["relative_humidity_2m"]
                cloud_coverage = hourly_data["cloud_cover_low"]
                radiation = hourly_data["shortwave_radiation"]

                kiev_tz = pytz.timezone("Europe/Kiev")
                utc_tz = pytz.utc

                for i in range(len(times)):
                    local_time = datetime.fromisoformat(times[i])
                    kiev_time = kiev_tz.localize(local_time)
                    utc_time = kiev_time.astimezone(utc_tz)
                    if utc_time.month == 3 and utc_time.day == 31:
                        if utc_time.hour == 1:  # The hour that doesn't exist
                            print(f"Skipping record due to DST transition: {utc_time}")
                            continue  # Skip this record since 1 AM does not exist
                    WeatherData.objects.create(
                        location=location,
                        time=utc_time,
                        temperature=temperatures[i],
                        relative_humidity=humidities[i],
                        cloud_coverage=cloud_coverage[i],
                        radiation_w_m2=radiation[i]
                    )

                messages.success(request, f"Погодні дані для {location.name} успішно завантажено")
            else:
                messages.error(request, f"Не знайдено даних для {location.name}")
            return redirect('fetch_weather')
    locations = Location.objects.all()
    return render(request, 'locations/fetch_weather.html', {'locations': locations})

