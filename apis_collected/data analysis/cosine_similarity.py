import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
# Get a list of companies (excluding 'ClarityJS')
companies = df.columns.drop('ClarityJS')

# Step 3: Create a binary matrix for API usage per company
# Initialize a DataFrame with 0s where rows are APIs and columns are companies
api_usage_matrix = pd.DataFrame(0, index=sorted(set(df.melt(var_name='Company', value_name='API')['API'].dropna())), columns=companies)

# Fill the matrix with 1s where APIs are used by companies
for company in companies:
    used_apis = df[company].dropna().unique()
    api_usage_matrix.loc[used_apis, company] = 1

# Step 4: Calculate cosine similarity between each pair of companies
cosine_sim_matrix = pd.DataFrame(cosine_similarity(api_usage_matrix.T), index=companies, columns=companies)

# Step 5: Visualize the cosine similarity matrix using a heatmap
fig = px.imshow(
    cosine_sim_matrix,
    labels=dict(x="Company", y="Company", color="Cosine Similarity"),
    x=cosine_sim_matrix.columns,
    y=cosine_sim_matrix.index,
    color_continuous_scale="Blues"
)

fig.update_layout(
    title='Cosine Similarity of API Usage Between Companies',
    xaxis_title='Company',
    yaxis_title='Company'
)

# Step 6: Show the plot
fig.write_image('plots/cosine_similarity.png', format='png', width=1200, height=600)
fig.show()
