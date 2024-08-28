import pandas as pd

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection_no_clarity.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
api_counts = df.melt(var_name='Company', value_name='API').dropna()

# Step 3: Extract API category (e.g., 'KeyboardEvent', 'MouseEvent', 'Touch', 'TouchEvent')
api_counts['Category'] = api_counts['API'].apply(lambda x: x.split('.')[0])

# Step 4: Group by company and category to count occurrences
category_counts = api_counts.groupby(['Company', 'Category']).size().reset_index(name='Count')

# Step 5: Filter out zero counts
category_counts = category_counts[category_counts['Count'] > 0]

# Step 6: Sort values in descending order for each company
category_counts = category_counts.sort_values(by=['Company', 'Count'], ascending=[True, False])

# Step 7: Generate LaTeX table string with company names, categories, and counts
latex_table = "\\begin{table}[h]\n\\centering\n\\begin{tabular}{|l|l|l|}\n\\hline\n"
latex_table += "Company & Event Type & Count \\\\\n\\hline\n"

for company, group in category_counts.groupby('Company'):
    # Add company name as the first column spanning multiple rows
    first_row = True
    for _, row in group.iterrows():
        if first_row:
            latex_table += f"{company} & {row['Category']} & {int(row['Count'])} \\\\\n"
            first_row = False
        else:
            latex_table += f" & {row['Category']} & {int(row['Count'])} \\\\\n"
    latex_table += "\\hline\n"

latex_table += "\\end{tabular}\n\\caption{API Event Counts per Company (Sorted in Descending Order)}\n\\end{table}"

# Display the LaTeX table
print(latex_table)

# Optionally, save the LaTeX table to a file
with open('tables/event_counts_per_company_sorted.tex', 'w') as f:
    f.write(latex_table)
