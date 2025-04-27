# Check and install the 'readr' package if not installed
if (!requireNamespace("readr", quietly = TRUE)) {
  install.packages("readr")
}

# Load the required libraries
library(dplyr)
library(readr)
library(openxlsx)

# List of files in your folder
files <- list.files(path = "preprocess1", pattern = "*.csv", full.names = TRUE)

# Function to read and clean each file
read_and_clean <- function(file_path) {
  data <- read_csv(file_path)  # Use read_csv to read CSV files
  
  # Ensure 'Timestamp' is in the correct format
  data$Timestamp <- as.POSIXct(data$Timestamp, format = "%Y-%m-%d %H:%M:%S")
  
  return(data)
}

# Read all files and clean them
list_of_data <- lapply(files, read_and_clean)

# Initialize the merged_data with the first dataset
merged_data <- list_of_data[[1]]

# Loop through the remaining files and merge them
for (i in 2:length(list_of_data)) {
  data <- list_of_data[[i]]
  
  # Merge by 'Timestamp' without creating suffixes
  # Use 'full_join()' to align the data by 'Timestamp'
  merged_data <- full_join(merged_data, data, by = "Timestamp")
  
  # After merging, we check for column name conflicts
  # We will rename any duplicated columns with a unique suffix to avoid name conflicts
  # Keep the original column names intact if they don't conflict
  new_column_names <- make.unique(names(merged_data))
  names(merged_data) <- new_column_names
}

# Sort the data by 'Timestamp'
merged_data <- merged_data %>% arrange(Timestamp)

# Save the merged data to a new Excel file
write.xlsx(merged_data, "merged_data1.xlsx")
