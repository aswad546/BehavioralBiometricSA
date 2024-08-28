import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)
# Step 2: Prepare the data
# Get a list of companies (excluding 'ClarityJS')
companies = df.columns.drop('ClarityJS')

# Create a binary matrix for API usage per company
api_usage_matrix = pd.DataFrame(
    0, 
    index=sorted(set(df.melt(var_name='Company', value_name='API')['API'].dropna())), 
    columns=companies
)

# Fill the matrix with 1s where APIs are used by companies
for company in companies:
    used_apis = df[company].dropna().unique()
    api_usage_matrix.loc[used_apis, company] = 1

# Step 3: Apply PCA for Dimensionality Reduction
pca = PCA()
pca.fit(api_usage_matrix.T)  # Transpose to get companies as rows

# Step 4: Calculate the explained variance ratio
explained_variance_ratio = pca.explained_variance_ratio_

# Step 5: Create a scree plot
num_components = list(range(1, len(explained_variance_ratio) + 1))  # Convert range to a list

fig = px.line(
    x=num_components,
    y=np.cumsum(explained_variance_ratio),
    labels={'x': 'Number of Components', 'y': 'Cumulative Explained Variance'},
    title='Scree Plot for PCA'
)

fig.add_scatter(
    x=num_components,  # Use the list here instead of range
    y=explained_variance_ratio,
    mode='lines+markers',
    name='Explained Variance Ratio'
)


fig.write_image('plots/elbow_plot.png', format='png', width=1200, height=600)
fig.show()
