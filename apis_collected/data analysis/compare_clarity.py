import pandas as pd

# Step 1: Read the CSV file into a DataFrame
file_path = 'dataset/behavioral_api_collection.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Step 2: Prepare the data
clarity_apis = set(df['ClarityJS'].dropna().unique())  # Unique APIs in 'ClarityJS' column
all_apis_except_clarity = set(df.drop(columns=['ClarityJS']).melt(var_name='Company', value_name='API').dropna()['API'].unique())  # Unique APIs in all other columns

# Step 3: Find the intersection and unique APIs
intersection_apis = clarity_apis.intersection(all_apis_except_clarity)
unique_to_clarity_apis = clarity_apis - all_apis_except_clarity

# Step 4: Output results in structured text format
print("APIs that overlap between ClarityJS and other scripts:")
for api in sorted(intersection_apis):
    print(f"- {api}")

print("\nAPIs unique to ClarityJS (not found in any other script):")
for api in sorted(unique_to_clarity_apis):
    print(f"- {api}")

# Step 5: Generate LaTeX table code to document the results

# Create a LaTeX table with overlapping APIs and unique APIs
latex_code = r"""
\documentclass{article}
\usepackage{booktabs}  % For professional looking tables
\usepackage{makecell}  % For wrapping text in cells

\begin{document}

\section*{API Analysis between ClarityJS and Other Scripts}

\subsection*{1. Overlapping APIs}

\begin{table}[h]
\centering
\begin{tabular}{|l|}
\hline
\textbf{APIs Overlapping with Other Scripts} \\
\hline
"""

# Add overlapping APIs to the table
for api in sorted(intersection_apis):
    latex_code += f"{api} \\\\\n"

latex_code += r"""
\hline
\end{tabular}
\caption{List of APIs that overlap between ClarityJS and other scripts.}
\end{table}

\newpage

\subsection*{2. Unique APIs to ClarityJS}

\begin{table}[h]
\centering
\begin{tabular}{|l|}
\hline
\textbf{APIs Unique to ClarityJS} \\
\hline
"""

# Add unique APIs to the table
for api in sorted(unique_to_clarity_apis):
    latex_code += f"{api} \\\\\n"

latex_code += r"""
\hline
\end{tabular}
\caption{List of APIs that are unique to ClarityJS and not found in any other script.}
\end{table}

\end{document}
"""

# Step 6: Save the LaTeX code to a file
with open('tables/api_analysis_clarityjs.tex', 'w') as f:
    f.write(latex_code)

print("\nLaTeX code for the table has been saved to 'api_analysis_clarityjs.tex'.")
