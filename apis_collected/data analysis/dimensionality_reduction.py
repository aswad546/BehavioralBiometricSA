import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

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

### Apply PCA for Dimensionality Reduction

# Step 3: Apply PCA with n_components=6
pca_6 = PCA(n_components=6)
pca_results_6 = pca_6.fit_transform(api_usage_matrix.T)  # Transpose to get companies as rows

# Step 4: Apply PCA with n_components=7
pca_7 = PCA(n_components=7)
pca_results_7 = pca_7.fit_transform(api_usage_matrix.T)  # Transpose to get companies as rows

# Create DataFrames with PCA results
pca_df_6 = pd.DataFrame(data=pca_results_6, index=companies)
pca_df_7 = pd.DataFrame(data=pca_results_7, index=companies)

# Step 5: Visualize PCA Results
# Visualize the first two principal components for n_components=6
fig_pca_6 = px.scatter(pca_df_6, x=0, y=1, text=pca_df_6.index)
fig_pca_6.update_traces(textposition='top center')
fig_pca_6.update_layout(title='2D PCA of API Usage (n_components=6)', xaxis_title='Principal Component 1', yaxis_title='Principal Component 2')
fig_pca_6.write_image('plots/pca_6.png', format='png', width=1200, height=600)
fig_pca_6.show()

# Visualize the first three principal components for n_components=7
fig_pca_7 = px.scatter_3d(pca_df_7, x=0, y=1, z=2, text=pca_df_7.index)
fig_pca_7.update_traces(textposition='top center')
fig_pca_7.update_layout(title='3D PCA of API Usage (n_components=7)', scene=dict(
    xaxis_title='Principal Component 1',
    yaxis_title='Principal Component 2',
    zaxis_title='Principal Component 3'
))
fig_pca_7.write_image('plots/pca_7.png', format='png', width=1200, height=600)
fig_pca_7.show()

### Apply t-SNE for Nonlinear Dimensionality Reduction

# Determine number of samples for t-SNE perplexity
n_samples = len(companies)

# Step 6: Apply t-SNE with n_components=2 for visualization
# Adjust perplexity to be less than n_samples
tsne_perplexity = min(30, n_samples - 1)

tsne_6 = TSNE(n_components=2, perplexity=tsne_perplexity, n_iter=300, random_state=42)
tsne_results_6 = tsne_6.fit_transform(pca_results_6)  # Use PCA results for initial dimension reduction

tsne_7 = TSNE(n_components=2, perplexity=tsne_perplexity, n_iter=300, random_state=42)
tsne_results_7 = tsne_7.fit_transform(pca_results_7)  # Use PCA results for initial dimension reduction

# Create DataFrames with t-SNE results
tsne_df_6 = pd.DataFrame(data=tsne_results_6, columns=['Dim1', 'Dim2'], index=companies)
tsne_df_7 = pd.DataFrame(data=tsne_results_7, columns=['Dim1', 'Dim2'], index=companies)

# Step 7: Visualize t-SNE Results
# 2D t-SNE plot for n_components=6
fig_tsne_6 = px.scatter(tsne_df_6, x='Dim1', y='Dim2', text=tsne_df_6.index)
fig_tsne_6.update_traces(textposition='top center')
fig_tsne_6.update_layout(title='t-SNE of API Usage (n_components=6)', xaxis_title='Dimension 1', yaxis_title='Dimension 2')
fig_tsne_6.write_image('plots/tsne_6.png', format='png', width=1200, height=600)
fig_tsne_6.show()

# 2D t-SNE plot for n_components=7
fig_tsne_7 = px.scatter(tsne_df_7, x='Dim1', y='Dim2', text=tsne_df_7.index)
fig_tsne_7.update_traces(textposition='top center')
fig_tsne_7.update_layout(title='t-SNE of API Usage (n_components=7)', xaxis_title='Dimension 1', yaxis_title='Dimension 2')
fig_tsne_7.write_image('plots/tsne_7.png', format='png', width=1200, height=600)
fig_tsne_7.show()
