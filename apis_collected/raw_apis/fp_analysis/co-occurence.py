import json
import pandas as pd
import plotly.express as px
import os

# Load the API usage data for companies from a JSON file
file_path = '/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis/fp_apis_per_company_with_counts.json'  # Update with the actual path to your API data file
with open(file_path, 'r') as f:
    api_usage_data = json.load(f)

# Convert the data into a DataFrame
df = pd.DataFrame(api_usage_data)

# Step 1: Prepare the data
# Get a list of companies (assuming 'ClarityJS' should be excluded)
companies = df.columns.drop('ClarityJS', errors='ignore')

# Step 2: Initialize a co-occurrence matrix for APIs
all_apis = df.index  # List of all APIs
co_occurrence_matrix = pd.DataFrame(0, index=all_apis, columns=all_apis)

# Step 3: Calculate co-occurrence counts for APIs
for company in companies:
    invoked_apis = df[company][df[company] > 0].index  # APIs invoked by the company
    for api1 in invoked_apis:
        for api2 in invoked_apis:
            if api1 != api2:  # Skip self-co-occurrence
                co_occurrence_matrix.loc[api1, api2] += 1

# Step 4: Filter the co-occurrence matrix to keep only APIs with at least one co-occurrence >= 2
filtered_matrix = co_occurrence_matrix[(co_occurrence_matrix >= 2).any(axis=1)]
filtered_matrix = filtered_matrix.loc[:, (filtered_matrix >= 2).any(axis=0)]  # Keep columns with at least one co-occurrence >= 2

# Step 5: Visualize the filtered co-occurrence matrix using a heatmap with Plotly
fig = px.imshow(
    filtered_matrix,
    labels=dict(x="API", y="API", color="Co-occurrence Count"),
    x=filtered_matrix.columns,
    y=filtered_matrix.index,
    color_continuous_scale="YlOrBr"
)

fig.update_layout(
    title='Filtered API Co-occurrence Matrix (At least one co-occurrence ≥ 2)',
    xaxis_title='API',
    yaxis_title='API'
)

# Step 6: Save the heatmap
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)
fig.write_image(os.path.join(output_dir, 'filtered_api_cooccurrence_heatmap.png'), format='png', width=1200, height=600)

# Show the heatmap
fig.show()
