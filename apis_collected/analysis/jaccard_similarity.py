import pandas as pd
import plotly.express as px
import numpy as np

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
# Get a list of companies (excluding 'ClarityJS')
companies = df.columns.drop('ClarityJS')

# Get unique APIs for each company
company_apis = {company: set(df[company].dropna().unique()) for company in companies}

# Step 3: Calculate Jaccard similarity between each pair of companies
jaccard_similarity = pd.DataFrame(index=companies, columns=companies)

for company1 in companies:
    for company2 in companies:
        if company1 == company2:
            jaccard_similarity.loc[company1, company2] = 1.0
        else:
            set1 = company_apis[company1]
            set2 = company_apis[company2]
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            jaccard_index = intersection / union if union != 0 else 0
            jaccard_similarity.loc[company1, company2] = jaccard_index

# Convert the DataFrame to numeric format for heatmap
jaccard_similarity = jaccard_similarity.astype(float)

# Step 4: Visualize the Jaccard similarity matrix using a heatmap
fig = px.imshow(
    jaccard_similarity,
    labels=dict(x="Company", y="Company", color="Jaccard Similarity"),
    x=jaccard_similarity.columns,
    y=jaccard_similarity.index,
    color_continuous_scale="Blues"
)

fig.update_layout(
    title='Jaccard Similarity of API Usage Between Companies',
    xaxis_title='Company',
    yaxis_title='Company'
)

# Step 5: Show the plot

fig.write_image('plots/jaccard_similarity_across_companies.png', format='png', width=1200, height=600)
fig.show()
