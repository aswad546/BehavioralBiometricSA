import os
import json

# Function to load the API data from fp_sources.json
def load_api_data(api_file_path):
    with open(api_file_path, 'r') as f:
        return json.load(f)

# Function to find all .apis files in the specified directory
def find_api_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.apis')]

# Function to parse APIs from the input file format
def parse_apis(file_content):
    # Preprocess the file content to replace the unnecessary quotes and curly braces
    cleaned_content = file_content.strip('{}').replace('""', '"')
    
    # Dictionary to track API call counts
    api_count = {}
    
    # Split the content by commas and extract API names (ignore the numeric prefixes)
    for entry in cleaned_content.split('","'):
        # Each entry looks like "2072,Window.String", so split by comma
        if ',' in entry:
            api_name = entry.split(',')[1].strip()
            # Count the number of times each API appears
            if api_name in api_count:
                api_count[api_name] += 1
            else:
                api_count[api_name] = 1
    
    return api_count

# Function to check if the file contains the APIs from fp_sources.json
def check_apis_in_file(file_path, apis_to_check):
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Parse APIs from the file and compare with APIs in fp_sources.json
    file_apis = parse_apis(file_content)
    
    # Filter out only the APIs that are in the fp_sources.json list
    matching_apis = {api: count for api, count in file_apis.items() if api in apis_to_check}
    
    return matching_apis

# Function to process all .apis files and save the matching results
def process_api_files(directory, api_file_path, output_file_path):
    # Load the APIs from fp_sources.json
    api_data = load_api_data(api_file_path)
    
    # Create a flattened set of APIs to check
    apis_to_check = set(api for sublist in api_data.values() for api in sublist)

    # Find all .apis files in the directory
    api_files = find_api_files(directory)
    
    # Dictionary to hold the results
    results = {}
    
    # Process each .apis file
    for api_file in api_files:
        file_path = os.path.join(directory, api_file)
        matching_apis = check_apis_in_file(file_path, apis_to_check)
        
        if matching_apis:
            # Store the results for this file, including the count of API calls
            results[api_file] = matching_apis
    
    # Write the results to the output file in JSON format
    with open(output_file_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)
    
    print(f"Processed {len(api_files)} files. Matching results saved to {output_file_path}")

# Main execution
if __name__ == "__main__":
    # Replace with the path to your directory containing .apis files
    directory = "/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis"  
    # Path to fp_sources.json file containing APIs
    api_file_path = "/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis/fp_sources.json"  
    # Output file to save the matching results
    output_file_path = "fp_apis_per_company_with_counts.json"  

    # Process the .apis files and generate the output
    process_api_files(directory, api_file_path, output_file_path)
