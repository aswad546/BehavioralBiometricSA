import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data from file (assuming it's in a JSON file)
file_path = '/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis/fp_apis_per_company_with_counts.json'  # Update this with the path to your file
with open(file_path, 'r') as f:
    data = json.load(f)

# Remove Clarity for analysis
if "Clarity" in data:
    del data["Clarity"]

plots_dir = "plots"

# Convert the data into a DataFrame
df = pd.DataFrame(data).fillna(0)

# Convert frequencies into binary values (0 if not called, 1 if called)
df_binary = df.applymap(lambda x: 1 if x > 0 else 0)

# 1. Find APIs invoked by all companies (common APIs)
common_apis = df_binary[df_binary.sum(axis=1) == len(df_binary.columns)]
print("APIs invoked by all companies (common APIs):")
print(common_apis.index.tolist())

# 2. Find unique APIs (invoked by only one company)
unique_apis = df_binary[df_binary.sum(axis=1) == 1]
print("\nAPIs invoked by only one company (unique APIs):")
print(unique_apis.index.tolist())

# 3. Cluster companies by their API invocation patterns
# Use hierarchical clustering to group companies
sns.clustermap(df_binary.T, cmap="coolwarm", metric='euclidean', method='ward')
plt.title('Hierarchical Clustering of Companies by API Invocation')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'clustering_companies_by_apis.png'))

# 4. Find top 5 most commonly invoked APIs (shared across companies)
top_apis = df_binary.sum(axis=1).sort_values(ascending=False).head(5)
print("\nTop 5 most commonly invoked APIs:")
print(top_apis)

# 5. Calculate the overlap of API usage between companies
api_overlap = df_binary.T.dot(df_binary)
plt.figure(figsize=(12, 8))
sns.heatmap(api_overlap, annot=True, cmap="YlGnBu", cbar=True)
plt.title('API Overlap Between Companies')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'api_overlap_between_companies.png'))

# Confirming visualizations
os.listdir(plots_dir)
