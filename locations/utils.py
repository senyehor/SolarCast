import requests


def fetch_forecast(latitude, longitude, start_date, end_date):
    """
    Fetch historical weather data for a location from Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":   latitude,
        "longitude":  longitude,
        "start_date": start_date,
        "end_date":   end_date,
        "hourly":     "temperature_2m,relative_humidity_2m,cloud_cover_low,shortwave_radiation",
        'timezone': 'Europe/Kiev'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()  # Returns the API response as JSON
    except requests.RequestException as e:
        return None

def fetch_weather_data(latitude, longitude, start_date, end_date):
    """
    Fetch historical weather data for a location from Open-Meteo API.
    """
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude":   latitude,
        "longitude":  longitude,
        "start_date": start_date,
        "end_date":   end_date,
        "hourly":     "temperature_2m,relative_humidity_2m,cloud_cover_low,shortwave_radiation",
        'timezone': 'Europe/Kiev'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()  # Returns the API response as JSON
    except requests.RequestException as e:
        return None

