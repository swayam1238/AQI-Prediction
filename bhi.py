import requests

def fetch_aqi_data(latitude, longitude, token):
    url = f"http://api.waqi.info/feed/geo:{latitude};{longitude}/?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'ok':
            print(data['data'])  # This will print all the data for the location
            return data['data']
        else:
            print("Error in API response:", data['status'])
    else:
        print(f"API request failed. HTTP Status Code: {response.status_code}")
    return None

# Test with your coordinates and token
latitude, longitude = 12.9716, 77.5946  # Example: Bangalore coordinates
token = 'fe95b78ed8a627a6a9d8c4c9db421652b8b9416a'
fetch_aqi_data(latitude, longitude, token)
