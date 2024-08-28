import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import pdist, squareform

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
# Get a list of companies (excluding 'ClarityJS')
companies = df.columns.drop('ClarityJS')

# Extract unique APIs used by each company
company_apis = {company: set(df[company].dropna().unique()) for company in companies}

# Step 3: Create a list of all unique APIs across all companies
all_apis = set()
for apis in company_apis.values():
    all_apis.update(apis)
all_apis = sorted(all_apis)  # Sort for consistent matrix indexing

# Step 4: Initialize a co-occurrence matrix
co_occurrence_matrix = pd.DataFrame(0, index=all_apis, columns=all_apis)

# Step 5: Calculate co-occurrence counts
for apis in company_apis.values():
    for api1 in apis:
        for api2 in apis:
            if api1 != api2:  # Skip self-co-occurrence
                co_occurrence_matrix.loc[api1, api2] += 1

# Step 6: Perform hierarchical clustering
distance_matrix = pdist(co_occurrence_matrix)  # Pairwise distance
linkage_matrix = sch.linkage(distance_matrix, method='ward')

# Step 7: Create a dendrogram and reorder the co-occurrence matrix
dendro = sch.dendrogram(linkage_matrix, labels=all_apis, no_plot=True)
dendro_order = dendro['leaves']
reordered_matrix = co_occurrence_matrix.iloc[dendro_order, :].iloc[:, dendro_order]

# Step 8: Plot the clustered heatmap with Plotly
dendro_top = ff.create_dendrogram(reordered_matrix.values, orientation='bottom', labels=reordered_matrix.columns)
dendro_side = ff.create_dendrogram(reordered_matrix.values, orientation='right', labels=reordered_matrix.index)

# Create a new figure for the heatmap and dendrograms
fig = go.Figure()

# Add the dendrogram for the columns (top)
for trace in dendro_top['data']:
    fig.add_trace(trace)

# Add the dendrogram for the rows (side)
for trace in dendro_side['data']:
    fig.add_trace(trace)

# Add heatmap
heatmap = go.Heatmap(
    x=dendro_top['layout']['xaxis']['tickvals'],
    y=dendro_side['layout']['yaxis']['tickvals'],
    z=reordered_matrix.values,
    colorscale='Blues'
)

fig.add_trace(heatmap)

# Update layout to integrate heatmap and dendrograms properly
fig.update_layout(
    width=800,
    height=800,
    xaxis={'domain': [.15, 1], 'mirror': True},
    yaxis={'domain': [0, .85], 'mirror': True},
    xaxis2={'domain': [0, .15], 'showticklabels': False, 'mirror': True},
    yaxis2={'domain': [.85, 1], 'showticklabels': False, 'mirror': True},
    showlegend=False,
    hovermode='closest',
    title='Clustered Heatmap of API Co-occurrence Across Companies'
)

# Save the plot as an image and show it
fig.write_image('plots/clustered_co-occurence_heatmap.png', format='png', width=1200, height=600)
fig.show()
