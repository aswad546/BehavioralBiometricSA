import pandas as pd
import numpy as np
import plotly.express as px

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
# Get a list of companies (excluding 'ClarityJS')
companies = df.columns.drop('ClarityJS')

# Extract unique APIs used by each company and categorize them
def categorize_api(api_name):
    return api_name.split('.')[0]  # Extract the event category (e.g., 'KeyboardEvent' from 'KeyboardEvent.key')

company_apis = {company: set(df[company].dropna().unique()) for company in companies}
company_categories = {company: set(categorize_api(api) for api in apis) for company, apis in company_apis.items()}

# Step 3: Create a list of all unique categories across all companies
all_categories = set()
for categories in company_categories.values():
    all_categories.update(categories)
all_categories = sorted(all_categories)  # Sort for consistent matrix indexing

# Step 4: Initialize a co-occurrence matrix for categories
co_occurrence_matrix = pd.DataFrame(0, index=all_categories, columns=all_categories)

# Step 5: Calculate co-occurrence counts for categories
for categories in company_categories.values():
    for category1 in categories:
        for category2 in categories:
            if category1 != category2:  # Skip self-co-occurrence
                co_occurrence_matrix.loc[category1, category2] += 1

# Step 6: Visualize the co-occurrence matrix using a heatmap
fig = px.imshow(
    co_occurrence_matrix,
    labels=dict(x="API Category", y="API Category", color="Co-occurrence Count"),
    x=co_occurrence_matrix.columns,
    y=co_occurrence_matrix.index,
    color_continuous_scale="Blues"
)

fig.update_layout(
    title='API Category Co-occurrence Matrix Across Companies',
    xaxis_title='API Category',
    yaxis_title='API Category'
)


# Step 7: Show the plot
fig.write_image('plots/api_co-occurence.png', format='png', width=1200, height=600)
fig.show()
