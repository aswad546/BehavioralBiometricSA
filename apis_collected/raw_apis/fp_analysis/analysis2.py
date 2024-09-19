import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data from file (assuming it's in a JSON file)
file_path = '/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis/fp_apis_per_company_with_counts.json'  # Update this with the path to your file
with open(file_path, 'r') as f:
    data = json.load(f)

# Create a new directory for saving plots
plots_dir = 'plots'
os.makedirs(plots_dir, exist_ok=True)

# Remove Clarity from the data for general analysis
if "Clarity" in data:
    del data["Clarity"]

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Replace NaNs with zeros (APIs not used by a company should be treated as 0)
df = df.fillna(0)

# Convert frequencies into binary values (0 if not called, 1 if called)
df_binary = df.applymap(lambda x: 1 if x > 0 else 0)

# 1. Heatmap of API invocation (binary) across companies
plt.figure(figsize=(12, 8))
sns.heatmap(df_binary.T, cmap="Greens", annot=False, cbar=True)
plt.title('Heatmap of API Invocation Across Companies (Excluding Clarity)')
plt.xlabel('API Calls')
plt.ylabel('Companies')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'heatmap_api_invocation.png'))

# 2. Bar chart of how many companies invoke each API
api_invocation_count = df_binary.sum(axis=1).sort_values(ascending=False)

plt.figure(figsize=(12, 8))
api_invocation_count.plot(kind='bar')
plt.title('Number of Companies Invoking Each API')
plt.xlabel('API Call')
plt.ylabel('Number of Companies')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'bar_api_invocation_count.png'))

# 3. Pie chart showing how many APIs are invoked by a specific company (example: 'Nudata')
company_name = 'Nudata'  # Update this to choose a different company
df_company_binary = df_binary[company_name][df_binary[company_name] > 0]  # APIs invoked by this company

plt.figure(figsize=(8, 8))
df_company_binary.plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.title(f'Proportion of APIs Invoked by {company_name}')
plt.ylabel('')  # Hide the y-label
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, f'pie_{company_name}_api_invocation.png'))

# 4. Histogram of how many companies share the same APIs
shared_api_count = df_binary.sum(axis=1)

plt.figure(figsize=(12, 8))
shared_api_count.value_counts().sort_index().plot(kind='bar')
plt.title('Distribution of API Sharing Among Companies')
plt.xlabel('Number of Companies Using the API')
plt.ylabel('Number of APIs')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'histogram_api_sharing.png'))

# 5. Bar chart showing the number of APIs invoked by each company
company_api_count = df_binary.sum()

plt.figure(figsize=(12, 8))
company_api_count.plot(kind='bar')
plt.title('Number of APIs Invoked by Each Company')
plt.xlabel('Companies')
plt.ylabel('Number of APIs')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'bar_company_api_count.png'))

# Confirm plots saved
os.listdir(plots_dir)
