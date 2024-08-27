import pandas as pd
import plotly.express as px
import plotly.colors

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection_no_clarity.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
api_counts = df.melt(var_name='Script', value_name='API').dropna()
api_counts = api_counts.groupby('API').size().reset_index(name='Total Count')

# Step 2.5: Sort the data by 'Total Count' in descending order and select the top 30
api_counts = api_counts.sort_values(by='Total Count', ascending=False).head(30)

# Step 3: Extract API category (e.g., 'KeyboardEvent', 'MouseEvent', 'Touch', 'TouchEvent')
api_counts['Category'] = api_counts['API'].apply(lambda x: x.split('.')[0])

# Step 4: Generate a color map automatically based on unique categories
unique_categories = api_counts['Category'].unique()
color_sequence = px.colors.qualitative.Plotly  # Using Plotly's qualitative color scale
color_map = {category: color_sequence[i % len(color_sequence)] for i, category in enumerate(unique_categories)}

# Step 5: Create a bar plot to show the total frequency of the top 30 APIs with automatic colors
fig = px.bar(
    api_counts,
    x='API',
    y='Total Count',
    color='Category',
    color_discrete_map=color_map,
    title='Top 30 Most Frequent APIs Across All Scripts with Automatic Group Colors'
)

# Step 6: Sort the x-axis based on the sorted 'API' order
fig.update_layout(xaxis={'categoryorder':'total descending'})

# Step 7: Save and display the plot
fig.write_image('plots/top_30_api_frequency_colored_bar_plot.png', format='png', width=1200, height=600)
fig.show()
