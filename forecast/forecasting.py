from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from keras.src.saving import load_model

from forecast.models import LocationModel
from forecast.utils import create_sequences_only_features, TIME_STEPS
from locations.models import Location
from locations.utils import fetch_forecast

_Forecast = list[tuple[str, float]]


class Forecaster:
    def __init__(self, location: Location, start: datetime, end: datetime):
        self.__location = location
        self.__start = start
        self.__end = end

    def get_forecast(self) -> _Forecast:
        weather_data = fetch_forecast(
            self.__location.latitude, self.__location.longitude,
            self.__start, self.__end
        )
        original_df = create_dataframe_from_forecast(weather_data)
        original_df = original_df.sort_values(by='time')
        df = original_df[original_df['shortwave_radiation'] > 0].copy()
        column_mapping = {
            'cloud_cover_low':      'cloud_coverage',
            'relative_humidity_2m': 'relative_humidity',
            'shortwave_radiation':  'radiation_w_m2',
            'temperature_2m':       'temperature'
        }
        df.rename(columns=column_mapping, inplace=True)
        features = df.drop(columns=['time']).copy()
        model_path = LocationModel.objects.get(location=self.__location).filename
        scaler_features = joblib.load(f'{model_path}.pkl')
        model = load_model(f'{model_path}.keras')
        features_normalized = scaler_features.transform(features)
        X = create_sequences_only_features(pd.DataFrame(features_normalized), TIME_STEPS)
        predictions = model.predict(X)
        predictions = np.expm1(predictions)
        original_df['forecasted_energy'] = 0
        non_zero_indices = df.index.values
        for idx, prediction in zip(non_zero_indices, predictions.flatten()):
            original_df.at[idx, 'forecasted_energy'] = prediction
        return [(row.time.strftime("%d-%m-%Y %H:%M"), round(row.forecasted_energy, 2)) for row in
                original_df.itertuples(index=False)]


def create_dataframe_from_forecast(json_data):
    if json_data and "hourly" in json_data:
        hourly_data = json_data["hourly"]
        df = pd.DataFrame(
            {
                'time':                 pd.to_datetime(hourly_data["time"]),
                'temperature_2m':       hourly_data["temperature_2m"],
                'relative_humidity_2m': hourly_data["relative_humidity_2m"],
                'cloud_cover_low':      hourly_data["cloud_cover_low"],
                'shortwave_radiation':  hourly_data["shortwave_radiation"]
            }
        )
        return df

