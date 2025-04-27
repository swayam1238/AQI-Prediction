import pandas as pd

# Load your Excel file
file_path = 'merged_data1.xlsx'  # replace with your file path
df = pd.read_excel(file_path)

# Identify columns to merge
merged_columns = {}

for col in df.columns:
    # Get the prefix (before the dot)
    prefix = col.split('.')[0]
    
    # If the prefix already exists in the dictionary, merge it
    if prefix in merged_columns:
        merged_columns[prefix].append(col)
    else:
        merged_columns[prefix] = [col]

# Merge columns with the same prefix
for prefix, columns in merged_columns.items():
    if len(columns) > 1:
        # Create a new column with the merged values (you can decide how to merge, here I just sum the values)
        df[prefix] = df[columns].sum(axis=1)
        # Drop the original columns after merging
        df.drop(columns, axis=1, inplace=True)

# Save the updated DataFrame to a new Excel file
df.to_excel('merged_columns_output1.xlsx', index=False)
