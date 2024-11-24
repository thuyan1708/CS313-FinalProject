import joblib
import pandas as pd
import numpy as np
import requests

BASE_API_URL = "https://efc1-35-240-221-166.ngrok-free.app/"

# Load the trained model
def load_sklearn_model(model_path):
    model = joblib.load(model_path)
    
    return model



def prepare_data_for_buy_sell_prediction(stock_data):
    stock_data['TradingDate'] = pd.to_datetime(stock_data['TradingDate'])
    stock_data = stock_data.sort_values('TradingDate')
    stock_data['RSI'] = calculate_rsi(stock_data['Close'])
    stock_data['MACD'], stock_data['MACD_signal'] = calculate_macd(stock_data['Close'])
    stock_data['BB_high'], stock_data['BB_low'] = calculate_bollinger_bands(stock_data['Close'])
    
    # Drop rows with NaN values caused by rolling calculations
    stock_data = stock_data.dropna()

    return stock_data

def predict_buy_sell_probability(model, stock_data):
    # Prepare data for prediction
    stock_data = prepare_data_for_buy_sell_prediction(stock_data)

    # Select the last row for prediction
    last_row = stock_data.iloc[-1]
    features = last_row[['Close', 'RSI', 'MACD', 'MACD_signal', 'BB_high', 'BB_low']].values.reshape(1, -1)

    # Predict probabilities
    buy_prob = model.predict_proba(features)[0][1] * 100  # Probability of "Buy" in percentage

    return buy_prob

    
# Manually Calculate RSI
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Manually Calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    macd_signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, macd_signal

# Manually Calculate Bollinger Bands
def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    rolling_mean = data.rolling(window).mean()
    rolling_std = data.rolling(window).std()
    bb_high = rolling_mean + (rolling_std * num_std_dev)
    bb_low = rolling_mean - (rolling_std * num_std_dev)
    return bb_high, bb_low

def predict_new_data(new_data: pd.DataFrame, features: list[str], window_size: int):
    """
    Preprocesses input data, sends it to the API for inference, and post-processes predictions.
    """
    # Sort and select the last window_size rows
    new_data = new_data.sort_values("TradingDate", ascending=True)
    last_window = new_data.iloc[-window_size:]

    # Extract feature values and normalize them
    X_last_window = last_window[features].values
    min_feature = np.min(X_last_window, axis=0)  # Column-wise min
    max_feature = np.max(X_last_window, axis=0)  # Column-wise max
    X_last_window_norm = (X_last_window - min_feature) / (max_feature - min_feature)

    # Reshape to match the LSTM input format (samples, timesteps, features)
    X_last_window_norm = X_last_window_norm.reshape(1, window_size, len(features))

    # Prepare payload for the API
    payload = {
        "X_inference_norm": X_last_window_norm.tolist()  # Convert NumPy array to JSON-compatible format
    }

    # Call the API endpoint
    response = requests.post(BASE_API_URL + "predict-next-day", json=payload)

    # Check if the API call is successful
    if response.status_code == 200:
        y_pred_norm = np.array(response.json()["predictions"])
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    # Denormalize the prediction
    y_pred_denorm = y_pred_norm * (max_feature[0] - min_feature[0]) + min_feature[0]

    return y_pred_denorm

def predict_3rd_day_open_price(new_data: pd.DataFrame, features: list[str], window_size: int):
    """
    Preprocesses input data, sends it to the API for 3rd-day open price inference, 
    and post-processes predictions.
    """
    # Sort and select the last window_size rows
    new_data = new_data.sort_values("TradingDate", ascending=True)
    last_window = new_data.iloc[-window_size:]

    # Extract feature values and normalize them
    X_last_window = last_window[features].values
    min_feature = np.min(X_last_window, axis=0)  # Column-wise min
    max_feature = np.max(X_last_window, axis=0)  # Column-wise max
    X_last_window_norm = (X_last_window - min_feature) / (max_feature - min_feature)

    # Reshape to match the LSTM input format (samples, timesteps, features)
    X_last_window_norm = X_last_window_norm.reshape(1, window_size, len(features))

    # Prepare payload for the API
    payload = {
        "X_inference_norm": X_last_window_norm.tolist()  # Convert NumPy array to JSON-compatible format
    }

    # Call the API endpoint
    response = requests.post(BASE_API_URL + "predict-3rd-day", json=payload)

    # Check if the API call is successful
    if response.status_code == 200:
        y_pred_norm = np.array(response.json()["predictions"])
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    # Denormalize the prediction
    y_pred_denorm = y_pred_norm * (max_feature[0] - min_feature[0]) + min_feature[0]

    return y_pred_denorm

def predict_3_consecutive_days_open_price(new_data: pd.DataFrame, features: list[str], window_size: int):
    """
    Preprocesses input data, sends it to the API for 3 consecutive days' open prices inference, 
    and post-processes predictions.
    """
    # Sort and select the last window_size rows
    new_data = new_data.sort_values("TradingDate", ascending=True)
    last_window = new_data.iloc[-window_size:]

    # Extract feature values and normalize them
    X_last_window = last_window[features].values
    min_feature = np.min(X_last_window, axis=0)  # Column-wise min
    max_feature = np.max(X_last_window, axis=0)  # Column-wise max
    X_last_window_norm = (X_last_window - min_feature) / (max_feature - min_feature)

    # Reshape to match the LSTM input format (samples, timesteps, features)
    X_last_window_norm = X_last_window_norm.reshape(1, window_size, len(features))

    # Prepare payload for the API
    payload = {
        "X_inference_norm": X_last_window_norm.tolist()  # Convert NumPy array to JSON-compatible format
    }

    response = requests.post(BASE_API_URL + "predict-3-consecutive-days", json=payload)

    # Check if the API call is successful
    if response.status_code == 200:
        y_pred_norm = np.array(response.json()["predictions"])
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    # Denormalize the predictions
    y_pred_denorm = y_pred_norm * (max_feature[0] - min_feature[0]) + min_feature[0]

    return y_pred_denorm
