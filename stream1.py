import streamlit as st
import numpy as np
import requests
from tensorflow.keras.models import load_model # type: ignore
import joblib

# Function to get AQI category
def get_aqi_category(aqi_value):
    if aqi_value <= 50:
        return "Good"
    elif 51 <= aqi_value <= 100:
        return "Moderate"
    elif 101 <= aqi_value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif 151 <= aqi_value <= 200:
        return "Unhealthy"
    elif 201 <= aqi_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

# Load pre-trained model and scaler
model = load_model("aqi_multi_output_model.h5", compile=False)
scaler = joblib.load('scaler.pkl')

# Function to fetch AQI data from the WAQI API with error handling
def fetch_aqi_data(latitude, longitude, token):
    url = f"http://api.waqi.info/feed/geo:{latitude};{longitude}/?token={token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'ok':
            return data['data']
        else:
            st.error("Error in API response: " + data.get('data', 'Unknown error'))
            return None
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred during API request: {err}")
    return None

# Function to get the user's location
def get_user_location():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        loc = data['loc'].split(',')
        latitude = float(loc[0])
        longitude = float(loc[1])
        return latitude, longitude
    except Exception as e:
        st.error("Error fetching user location. Defaulting to Bangalore.")
        return 12.9716, 77.5946  # Default to Bangalore

# Define prediction logic for different time intervals
def get_predictions_for_future_hours(input_data, model, scaler, hours_list):
    predictions = {}
    for hours in hours_list:
        pred = []
        temp_input = input_data.copy()
        for i in range(hours):
            prediction = model.predict(temp_input)
            pred.append(prediction[0])
            if i < hours - 1:
                temp_input[0, i+1, 0:10] = prediction[0, :10]
                temp_input[0, i+1, 1:] = temp_input[0, i, 1:]
        predictions[hours] = np.array(pred)
    return predictions

# Main app layout
st.set_page_config(page_title="Pollusense", page_icon="🌿", layout="wide")

# Sidebar for navigation between tabs
tabs = st.sidebar.radio("Navigation", ["Real-Time AQI", "Evaluation & Metrics"])

# Styling for dark theme
st.markdown("""
<style>
body {
    background-color: #1e1e1e;
    color: #ffffff;
}
.title { font-size: 2.5rem; font-weight: bold; color: #32cd32; text-align: center; }
.header { font-size: 1.5rem; font-weight: bold; color: #32cd32; }
.section-header { font-size: 1.3rem; font-weight: bold; color: #87cefa; }
.card { border-radius: 10px; padding: 15px; background-color: #2e2e2e; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); }
.card-title { font-size: 1.25rem; font-weight: bold; color: #00ced1; }
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<div class="title">Pollusense: Real-Time AQI and Prediction</div>', unsafe_allow_html=True)

# Real-time AQI Tab
if tabs == "Real-Time AQI":
    latitude, longitude = get_user_location()
    st.write(f"Location: Latitude {latitude}, Longitude {longitude}")

    # Fetch real-time data
    aqi_data = fetch_aqi_data(latitude, longitude, '192f9a616c7e9fc85f4a571fa4e415ed090f6d0e')
    if aqi_data:
        pollutants = ["aqi"]
        real_time_values = [aqi_data['aqi']]
        for pollutant, value in aqi_data['iaqi'].items():
            if pollutant not in ['t', 'wind', 'wg', 'w']:
                pollutants.append(pollutant)
                real_time_values.append(value['v'])

        while len(real_time_values) < 10:
            real_time_values.append(0)

        # Prepare input data
        input_data = np.zeros((1, 24, 20))
        input_data[0, :, 0:10] = np.tile(real_time_values[:10], (24, 1))
        for i in range(24):
            input_data[0, i, :] = scaler.transform(input_data[0, i, :].reshape(1, -1))

        # Get predictions for 1 hour, 6 hours, and 18 hours
        hours_list = [1, 6, 18]
        future_predictions = get_predictions_for_future_hours(input_data, model, scaler, hours_list)

        st.markdown("### Real-Time Data")
        real_time_table = {pollutant: [real_time_values[i]] for i, pollutant in enumerate(pollutants[:10])}
        st.table(real_time_table)
        
        st.markdown(f"### Air Quality Predictions for the Next 1, 6, and 18 Hours")
        prediction_table = {}
        for i in range(3):
            hour = [1, 6, 18][i]
            prediction_table[f"Hour {hour}"] = {f"{pollutant}": f"{future_predictions[hour][i, j]:.2f}" for j, pollutant in enumerate(pollutants[:10])}

        st.table(prediction_table)

    else:
        st.error("Failed to fetch AQI data.")

# Evaluation & Metrics Tab
elif tabs == "Evaluation & Metrics":
    st.markdown("<div class='section-header'>Model Evaluation Metrics</div>", unsafe_allow_html=True)

    rmse = 0.037
    mse = 0.0014
    mae = 0.018
    r2 = 0.8281

    st.write(f"**Root Mean Squared Error (RMSE):** {rmse}")
    st.write(f"**Mean Squared Error (MSE):** {mse}")
    st.write(f"**Mean Absolute Error (MAE):** {mae}")
    st.write(f"**R-squared (R²):** {r2}")
    
    st.markdown("<div class='section-header'>Evaluation Visualizations</div>", unsafe_allow_html=True)

    image_paths = [
        "pm10.png",
        "so2.png",
        "no2.png",
    ]
    
    for path in image_paths:
        st.image(path, use_column_width=True, caption=f"Visualization from {path}")
