import pandas as pd

# Load the Excel files
file1 = 'merged_columns_output.xlsx'
file2 = 'merged_columns_output1.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Standardize column names
df1.rename(columns={'Datetime': 'Datetime'}, inplace=True)  # Rename to a common name if needed
df2.rename(columns={'Timestamp': 'Datetime'}, inplace=True)  # Rename to the same column name

# Keep only the first 11 columns of the second dataframe
df2 = df2.iloc[:, :11]

# Merge the dataframes
merged_df = pd.merge(df1, df2, on='Datetime', how='outer')  # Use 'outer' for a full join; adjust as needed

# Sort by the 'Datetime' column
merged_df.sort_values(by='Datetime', inplace=True)

# Save the result to a new Excel file
output_file = 'mergedfinal.xlsx'
merged_df.to_excel(output_file, index=False)

print(f"Merged and sorted data saved to {output_file}.")
