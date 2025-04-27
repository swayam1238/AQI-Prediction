import os
import pandas as pd

def preprocess_aqi_data(file_path, output_folder):
    try:
        # Extract parts from the file name
        file_name = os.path.basename(file_path)
        file_parts = file_name.split('_')
        
        # Extract year and first month from file name
        year = int(file_parts[2])  # First year after "AQI_Hourly"
        month = file_parts[3]  # First month (assumed to be in full or abbreviated form)
        
        # Extract station name (all words between first "Month" and the second occurrence of "month")
        station_index_start = 4  # Station name starts after year and first month
        station_index_end = -2  # Ends two parts before the second month-year pair
        station_name = " ".join(file_parts[station_index_start:station_index_end]).replace("KSPCB", "").strip()
        
        # Load the dataset
        data = pd.read_excel(file_path)
        
        # Reshape into long format
        data_long = data.melt(id_vars=['Date'], var_name='Time', value_name='AQI')
        
        # Ensure proper date formatting
        month_num = pd.to_datetime(month, format='%B').month  # Convert month name to number
        data_long['Date'] = data_long['Date'].astype(str).str.zfill(2)  # Ensure day has 2 digits
        data_long['Datetime'] = pd.to_datetime(
            f"{year}-{month_num}-" + data_long['Date'] + " " + data_long['Time'],
            errors='coerce'
        )
        
        # Drop unnecessary columns and add station name
        data_long = data_long[['Datetime', 'AQI']]
        data_long[station_name] = data_long.pop('AQI')
        
        # Handle missing values
        data_long[station_name] = data_long[station_name].fillna(data_long[station_name].mean())
        
        # Save the processed file
        output_path = os.path.join(output_folder, f"Processed_{file_name}")
        data_long.to_excel(output_path, index=False)
        
        print(f"Processed file saved to: {output_path}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def process_all_files_in_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if file_name.endswith('.xlsx'):
            preprocess_aqi_data(file_path, output_folder)

# Example usage
input_folder = "Preprocess"
output_folder = "processed"
process_all_files_in_folder(input_folder, output_folder)
