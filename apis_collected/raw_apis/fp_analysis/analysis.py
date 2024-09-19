import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


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

# 1. Bar plot of total API usage frequency across all companies
df['Total_Frequency'] = df.sum(axis=1)
df_sorted = df.sort_values(by="Total_Frequency", ascending=False)

plt.figure(figsize=(12, 8))
df_sorted['Total_Frequency'].plot(kind='bar')
plt.title('Total Frequency of API Usage Across All Companies (Excluding Clarity)')
plt.xlabel('API Call')
plt.ylabel('Total Frequency of Usage')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'bar_total_frequency.png'))

# 2. Heatmap of API usage across companies
plt.figure(figsize=(12, 8))
sns.heatmap(df.T, cmap="Blues", annot=False, cbar=True)
plt.title('Heatmap of API Usage Across Companies (Excluding Clarity)')
plt.xlabel('API Calls')
plt.ylabel('Companies')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'heatmap_api_usage.png'))

# 3. Pie chart of the proportion of API usage by a specific company (example: 'Nudata')
company_name = 'Nudata'  # Update this to choose a different company
df_company = df[company_name][df[company_name] > 0]  # APIs used by this company

plt.figure(figsize=(8, 8))
df_company.plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.title(f'Proportion of APIs Used by {company_name}')
plt.ylabel('')  # Hide the y-label
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, f'pie_{company_name}_api_usage.png'))

# 4. Box plot of API usage distribution across companies
plt.figure(figsize=(12, 8))
sns.boxplot(data=df.T, palette="coolwarm")
plt.title('Distribution of API Usage Across Companies')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'boxplot_api_distribution.png'))

# 5. Scatter plot of specific API usage across companies
api_name = 'Navigator.userAgent'  # Update this to any specific API you'd like to inspect
df_api = df.loc[api_name]

plt.figure(figsize=(10, 6))
plt.scatter(x=df.columns, y=df_api)
plt.title(f'Scatter Plot of {api_name} Usage Across Companies')
plt.xlabel('Companies')
plt.ylabel('Frequency of Usage')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, f'scatter_{api_name}.png'))

# Confirm plots saved
os.listdir(plots_dir)
