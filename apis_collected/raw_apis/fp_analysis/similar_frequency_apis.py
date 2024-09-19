import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Load data from file (assuming it's in a JSON file)
file_path = '/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis/fp_apis_per_company_with_counts.json'  # Update this with the path to your file
with open(file_path, 'r') as f:
    data = json.load(f)

# Create directory for plots if it doesn't exist
plots_dir = "plots"
os.makedirs(plots_dir, exist_ok=True)

# Remove Clarity from the data for this analysis
if "Clarity" in data:
    del data["Clarity"]

# Convert the data into a DataFrame and fill NaN values with 0
df = pd.DataFrame(data).fillna(0)

# 1. Filter to get APIs that are invoked by all companies (i.e., non-zero for all companies)
api_invoked_by_all = df[df.gt(0).all(axis=1)]

# 2. Calculate the standard deviation of the frequency of each API across companies
api_std = api_invoked_by_all.std(axis=1)

# 3. Sort APIs by standard deviation (smallest variance means most similar frequency of calls)
similar_apis = api_std.sort_values()

# Display the top 5 APIs with the most similar frequency of calls across companies
print("APIs with the most similar frequency of calls across companies:")
print(similar_apis.head(5))

# 4. Plot the top 25 APIs with the most similar frequency
top_25_similar_apis = similar_apis.head(25)

plt.figure(figsize=(10, 6))
top_25_similar_apis.plot(kind='bar', color='purple')
plt.title('Top 25 APIs with Most Similar Frequency of Calls Across Companies (Excluding Clarity)')
plt.xlabel('API')
plt.ylabel('Standard Deviation of Frequency')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'similar_frequency_apis_invoked_by_all.png'))

# Show the plot
plt.show()
