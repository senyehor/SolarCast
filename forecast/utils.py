from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from keras import Input, Sequential
from keras.src.layers import Dense, Dropout, LSTM
from keras.src.optimizers import Adam
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from forecast.models import LocationModel
from locations.models import Location, SolarGenerationData, WeatherData


def create_sequences(features, target, time_steps):
    X, y = [], []
    for i in range(len(features) - time_steps):
        X.append(features[i:i + time_steps].values)
        y.append(target[i + time_steps])
    return np.array(X), np.array(y)


def create_sequences_only_features(features, time_steps):
    X = []
    for i in range(len(features) - time_steps):
        X.append(features[i:i + time_steps].values)
    return np.array(X)


TIME_STEPS = 9


def create_model_for_location(location: Location):
    solar_data = [
        {
            'time':   _.interval_start,
            'energy': _.generated_energy
        }
        for _ in
        SolarGenerationData.objects.filter(location=location).all().order_by('interval_start')
    ]
    weather_data = [
        {
            'time':              _.time,
            'temperature':       _.temperature,
            'relative_humidity': _.relative_humidity,
            'cloud_coverage':    _.cloud_coverage,
            'radiation_w_m2':    _.radiation_w_m2
        }
        for _ in
        WeatherData.objects.filter(
            location=location, time__gte=solar_data[0]['time'], time__lte=solar_data[-1]['time']
        )
    ]
    solar_df = pd.DataFrame(solar_data)
    weather_df = pd.DataFrame(weather_data)
    merged_data = pd.merge(solar_df, weather_df, on='time', how='inner')
    merged_data = merged_data[merged_data['radiation_w_m2'] > 0]
    merged_data['log_energy'] = np.log1p(merged_data['energy'])

    features = merged_data.drop(columns=['time', 'energy', 'log_energy'])
    target = merged_data['log_energy']

    scaler_features = MinMaxScaler()
    scaler_target = MinMaxScaler()

    features_normalized = scaler_features.fit_transform(features)
    target_normalized = scaler_target.fit_transform(target.values.reshape(-1, 1))

    features_normalized = pd.DataFrame(features_normalized, columns=features.columns)
    target_normalized = pd.Series(target_normalized.flatten(), name='solar_generation')

    # Generate sequences
    X, y = create_sequences(features_normalized, target_normalized, TIME_STEPS)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )

    # Build LSTM model
    model = Sequential()
    model.add(Input(shape=(X.shape[1], X.shape[2])))
    model.add(LSTM(64, return_sequences=True))
    model.add(Dropout(0.2))  # Dropout to prevent overfitting
    model.add(LSTM(64))
    model.add(Dropout(0.2))
    model.add(Dense(1))  # Output layer for regression
    learning_rate = 0.001  # You can experiment with different values
    optimizer = Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss='mean_squared_error')

    history = model.fit(
        X_train,
        y_train,
        batch_size=32,  # You can adjust this based on your dataset size and available memory
        epochs=100,  # You can adjust the number of epochs
        validation_data=(X_test, y_test),
        # Optional: to validate the model on test data during training
        verbose=1  # To see the training progress
    )
    predictions = model.predict(X_test)
    predictions = scaler_target.inverse_transform(predictions)

    y_test_inverse = scaler_target.inverse_transform(y_test.reshape(-1, 1))

    mae = mean_absolute_error(y_test_inverse, predictions)
    mse = mean_squared_error(y_test_inverse, predictions)

    folder = 'models/'
    filename = f'{folder}{location.id}'
    LocationModel.objects.update_or_create(
        location=location, defaults={'filename':   filename,
                                     'created_at': datetime.utcnow()}
    )
    model.save(filename + '.keras')
    joblib.dump(scaler_features, filename + '.pkl')
    return mae, mse

