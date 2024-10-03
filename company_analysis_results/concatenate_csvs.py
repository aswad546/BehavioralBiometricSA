import os
import pandas as pd

# Path to the directory containing folders
directory_path = "/home/vagrant/BehavioralBiometricSA/company_analysis_results"

# List to store individual dataframes
df_list = []

# Loop over all folders in the main directory
for folder_name in os.listdir(directory_path):
    folder_path = os.path.join(directory_path, folder_name)
    
    # Check if the folder contains the CSV file
    if os.path.isdir(folder_path):  # Ensure it's a directory
        csv_file_path = os.path.join(folder_path, "multicore_static_info.csv")
        
        # If the CSV file exists in the folder
        if os.path.exists(csv_file_path):
            # Read the CSV file and append it to the list
            df = pd.read_csv(csv_file_path)
            df_list.append(df)

# Concatenate all dataframes into one
combined_df = pd.concat(df_list, ignore_index=True)

# Save the final concatenated CSV
combined_df.to_csv("/home/vagrant/BehavioralBiometricSA/company_analysis_results/combined_multicore_static_info.csv", index=False)

print("All CSV files have been concatenated successfully!")
