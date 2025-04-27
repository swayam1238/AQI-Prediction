import streamlit as st
import numpy as np
import requests
from keras.models import load_model 
import joblib
from twilio.rest import Client

# Twilio credentials
TWILIO_ACCOUNT_SID = 'ACad5ceaf5affb3b2be62a499f99e6c599'
TWILIO_AUTH_TOKEN = '5a910855cf37aa218a452436e00926f5'
TWILIO_PHONE_NUMBER = '+12184293454'
USER_PHONE_NUMBER = '+919448265129'

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

def send_sms_notification(predictions, pollutants, hours):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = "Air Quality Prediction for the next few hours:\n\n"
    for i in range(hours):
        message += f"Hour {i + 1} Prediction:\n"
        aqi = predictions[i, 0]
        aqi_category = get_aqi_category(aqi)
        message += f"AQI: {aqi:.2f} ({aqi_category})\n"
        for j, pollutant in enumerate(pollutants[1:]):
            message += f"{pollutant}: {predictions[i, j + 1]:.2f}\n"
        message += "\n"

    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=USER_PHONE_NUMBER
        )
        st.success("SMS notification sent with air quality predictions.")
    except Exception as e:
        st.error(f"Failed to send SMS notification: {e}")

# Load pre-trained model and scaler
model = load_model("aqi_multi_output_model.h5", compile=False)
scaler = joblib.load('scaler.pkl')

def fetch_aqi_data(latitude, longitude, token):
    url = f"http://api.waqi.info/feed/geo:{latitude};{longitude}/?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'ok':
            return data['data']
        else:
            st.error("Error in API response.")
    else:
        st.error(f"API request failed. HTTP Status Code: {response.status_code}")
    return None

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
        return 12.9716, 77.5946

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
    aqi_data = fetch_aqi_data(latitude, longitude, 'fe95b78ed8a627a6a9d8c4c9db421652b8b9416a')
    if aqi_data:
        pollutants = ["aqi"]
        real_time_values = [aqi_data['aqi']]
        for pollutant, value in aqi_data['iaqi'].items():
            pollutants.append(pollutant)
            real_time_values.append(value['v'])

        while len(real_time_values) < 10:
            real_time_values.append(0)

        st.markdown("### Real-Time Data")
        real_time_table = {pollutant: [real_time_values[i]] for i, pollutant in enumerate(pollutants[:10])}
        st.table(real_time_table)

        # Prepare input data for prediction
        input_data = np.zeros((1, 24, 20))
        input_data[0, :, 0:10] = np.tile(real_time_values[:10], (24, 1))
        for i in range(24):
            input_data[0, i, :] = scaler.transform(input_data[0, i, :].reshape(1, -1))

        predictions = model.predict(input_data)
        num_hours = min(len(predictions), 10)

        st.markdown("### Predicted Data")
        prediction_table = {f"Hour {i+1}": {pollutant: f"{predictions[i, j]:.2f}" for j, pollutant in enumerate(pollutants[:10])} for i in range(num_hours)}
        st.table(prediction_table)

        send_sms_notification(predictions, pollutants, num_hours)
    else:
        st.error("Failed to fetch AQI data.")

# Evaluation & Metrics Tab
elif tabs == "Evaluation & Metrics":
    st.markdown("<div class='section-header'>Model Evaluation Metrics</div>", unsafe_allow_html=True)

    # Evaluation metrics
    rmse = 0.037
    mse = 0.0014
    mae = 0.018
    r2 = 0.707
    evs = 0.709
    accuracy = 81.81

    st.write(f"**Root Mean Squared Error (RMSE):** {rmse}")
    st.write(f"**Mean Squared Error (MSE):** {mse}")
    st.write(f"**Mean Absolute Error (MAE):** {mae}")
    st.write(f"**R-squared (R²):** {r2}")
    st.write(f"**Explained Variance Score (EVS):** {evs}")
    st.write(f"**Accuracy Percentage:** {accuracy}%")

    # Add images for visualization
    st.markdown("<div class='section-header'>Evaluation Visualizations</div>", unsafe_allow_html=True)
    
    # Paths to the images (replace these with your actual image paths)
    image_paths = [
        "path_to_image1.jpg",
        "path_to_image2.jpg",
        "path_to_image3.jpg",
        "path_to_image4.jpg",
        "path_to_image5.jpg"
    ]
    
    # Display images
    for path in image_paths:
        st.image(path, use_column_width=True, caption=f"Visualization from {path}")
