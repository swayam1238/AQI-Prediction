library(dplyr)
library(readxl)
library(openxlsx)

# List of files in your folder
files <- list.files(path = "processed", pattern = "*.xlsx", full.names = TRUE)

# Function to read and clean each file
read_and_clean <- function(file_path) {
  data <- read_excel(file_path)
  
  # Ensure 'Datetime' is in the correct format
  data$Datetime <- as.POSIXct(data$Datetime, format="%Y-%m-%d %H:%M:%S")
  
  return(data)
}

# Read all files and clean them
list_of_data <- lapply(files, read_and_clean)

# Initialize the merged_data with the first dataset
merged_data <- list_of_data[[1]]

# Loop through the remaining files and merge them
for (i in 2:length(list_of_data)) {
  data <- list_of_data[[i]]
  
  # Merge by 'Datetime' without creating suffixes
  # Use 'full_join()' to align the data by 'Datetime'
  merged_data <- full_join(merged_data, data, by = "Datetime")
  
  # After merging, we check for column name conflicts
  # We will rename any duplicated columns with a unique suffix to avoid name conflicts
  # Keep the original column names intact if they don't conflict
  new_column_names <- make.unique(names(merged_data))
  names(merged_data) <- new_column_names
}

# Sort the data by 'Datetime'
merged_data <- merged_data %>% arrange(Datetime)

# Save the merged data to a new Excel file
write.xlsx(merged_data, "merged_data.xlsx")
