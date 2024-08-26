import pandas as pd
import plotly.express as px
##Bar plot code
# # Step 1: Read the CSV file into a DataFrame
# file_path = 'behavioral_api_collection_no_clarity.csv'  # Replace with your actual file path
# df = pd.read_csv(file_path)

# # Step 2: Prepare the data
# api_counts = df.melt(var_name='Script', value_name='API').dropna()
# api_counts = api_counts.groupby('API').size().reset_index(name='Total Count')

# # Step 3: Create a bar plot to show the total frequency of each API
# fig = px.bar(api_counts, x='API', y='Total Count', title='Total Frequency of Each API Across All Scripts')

# # Step 4: Save and display the plot
# fig.write_image('api_frequency_bar_plot.png', format='png', width=1200, height=600)
# fig.show()

# # Stacked bar plot
# # Step 1: Read the CSV file into a DataFrame
# file_path = 'behavioral_api_collection.csv'  # Replace with your actual file path
# df = pd.read_csv(file_path)

# # Step 2: Prepare the data for a stacked bar plot
# api_counts_per_script = df.melt(var_name='Script', value_name='API').dropna()
# api_counts_per_script = api_counts_per_script.groupby(['API', 'Script']).size().reset_index(name='Count')

# # Step 3: Create a stacked bar plot to show the frequency of each API call per script
# fig = px.bar(api_counts_per_script, x='API', y='Count', color='Script', title='API Call Frequency Per Script', barmode='stack')

# # Step 4: Save and display the plot
# fig.write_image('stacked_api_frequency_bar_plot.png', format='png', width=1200, height=600)
# fig.show()


# # Stacked bar for API call frequency

# # Step 1: Read the CSV file into a DataFrame
# file_path = 'behavioral_api_collection_no_clarity.csv'  # Replace with your actual file path
# df = pd.read_csv(file_path)

# # Step 2: Prepare the data in binary format for a stacked bar chart
# df_binary = df.melt(var_name='Script', value_name='API').dropna()
# df_binary['Exists'] = 1  # Set all to 1 as we will pivot this to a binary matrix

# # Pivot the data to create a binary matrix of APIs (rows) vs Scripts (columns)
# df_binary_pivot = df_binary.pivot_table(index='API', columns='Script', values='Exists', fill_value=0)

# # Step 3: Prepare the data for Plotly
# df_binary_pivot = df_binary_pivot.reset_index().melt(id_vars='API', var_name='Script', value_name='Exists')

# # Step 4: Create a stacked bar chart using Plotly
# fig = px.bar(df_binary_pivot, x='Script', y='Exists', color='API', 
#              title='Stacked Bar Chart of API Presence Across Scripts',
#              labels={'Exists': 'API Presence', 'Script': 'Script Name', 'API': 'API Name'},
#              barmode='stack')

# # Step 5: Customize the layout for better visualization
# fig.update_layout(xaxis_tickangle=-45, height=600, width=1200, showlegend=True)

# # Step 6: Save and display the plot
# fig.write_image('stacked_bar_chart_api_presence.png', format='png', width=1200, height=600)
# fig.show()



import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# Load the CSV file (adjust the file path as needed)
file_path = 'behavioral_api_collection.csv'
data = pd.read_csv(file_path)

# Calculate the frequency of each API per company
api_company_frequency = data.apply(pd.Series.value_counts).fillna(0)

# Select top 30 APIs by total frequency across all companies to reduce clutter
top_apis = api_company_frequency.sum(axis=1).sort_values(ascending=False).index
api_company_top = api_company_frequency.loc[top_apis]

# Automatically detect API categories by extracting prefixes
api_prefixes = [api.split('.')[0] for api in api_company_top.index]

# Get unique prefixes
unique_prefixes = list(set(api_prefixes))

# Generate a list of distinct colors using matplotlib's color map
color_map = plt.cm.get_cmap('tab10', len(unique_prefixes))  # 'tab10' is a color map with 10 distinct colors
colors = [mcolors.rgb2hex(color_map(i)) for i in range(color_map.N)]

# Create a dictionary mapping each unique prefix to a distinct color
api_categories = {prefix: colors[i] for i, prefix in enumerate(unique_prefixes)}

# Radial Bar Plot (Polar Coordinates)
fig_radial = go.Figure()

for i, company in enumerate(api_company_top.columns):
    fig_radial.add_trace(go.Barpolar(
        r=api_company_top[company].values,
        theta=api_company_top.index,
        name=company,
        marker=dict(color=colors[i % len(colors)], line=dict(color='black', width=1))
    ))

fig_radial.update_layout(
    title='Radial Bar Plot of API Usage Across Companies',
    polar=dict(
        radialaxis=dict(showticklabels=False, ticks=''),
        angularaxis=dict(tickmode='array', tickvals=np.arange(0, 360, 10), ticks='')
    ),
    showlegend=True
)

fig_radial.show()

# Sunburst Chart for Hierarchical Representation of API Categories
# Reset the index to use it in the Sunburst chart
api_company_top = api_company_top.reset_index()

# Rename columns for clarity
api_company_top.rename(columns={'index': 'API'}, inplace=True)

# Extract the API category from the API names
api_company_top['category'] = api_company_top['API'].str.split('.').str[0]

# Prepare data for Sunburst plot
sunburst_data = api_company_top.melt(id_vars=['category', 'API'], var_name='Company', value_name='Frequency')

fig_sunburst = px.sunburst(
    sunburst_data,
    path=['category', 'API', 'Company'],
    values='Frequency',
    color='category',
    color_discrete_map={prefix: colors[i] for i, prefix in enumerate(unique_prefixes)},
    title='Sunburst Chart of API Usage by Category and Company'
)

fig_sunburst.show()
