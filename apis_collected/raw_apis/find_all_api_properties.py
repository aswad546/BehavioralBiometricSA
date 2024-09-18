import json

# Function to load the JSON data from a file
def load_data_from_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Recursive function to find all descendants of a parent class
def find_all_descendants(data, parent_class, property_name):
    result = []
    
    # Iterate through the data to find all children of the parent_class
    for class_name, details in data.items():
        if details.get("parent") == parent_class:
            # Add the current child class with the inherited property
            result.append(f"{class_name}.{property_name}")
            # Recursively find children of this class
            result.extend(find_all_descendants(data, class_name, property_name))
    
    return result

# Function to find the property in the class hierarchy
def find_property_in_hierarchy(data, class_name, property_name):
    # Traverse upwards in the class hierarchy
    while class_name:
        # Check if the class contains the property
        class_data = data.get(class_name, {})
        if property_name in class_data.get('properties', []) or \
           property_name in class_data.get('methods', []) or \
           property_name in class_data.get('members', []):
            # If found, return the class where it was found
            return class_name
        # Move up to the parent class
        class_name = class_data.get('parent', None)
    
    # If the property is not found in the hierarchy, return None
    return None

# Function to start the process of finding descendants, even if the property is not found
def find_children_with_property(data, parent_class, property_name):
    # Find if the property exists in the class or its parent hierarchy
    found_in_class = find_property_in_hierarchy(data, parent_class, property_name)
    
    if not found_in_class:
        # If the property is not found, use the original class but continue to find descendants
        print(f"{property_name} not found in {parent_class}. Adding class and descendants anyway.")
        found_in_class = parent_class  # Use the original class

    # Start the recursive search for all descendants from the class where the property was found or the original class
    descendants = find_all_descendants(data, found_in_class, property_name)

    # Include the original parent class property in the result
    return [f"{found_in_class}.{property_name}"] + descendants

# Function to process the ClassName.property from the input file and generate the output
def process_properties(input_file, output_file, data):
    results = {}
    total_pairs = 0  # To keep track of how many class-property pairs are saved

    with open(input_file, 'r') as infile:
        for line in infile:
            class_property = line.strip()  # Read each ClassName.property
            if '.' in class_property:
                parent_class, property_name = class_property.split('.')
                # Process and find descendants
                try:
                    result = find_children_with_property(data, parent_class, property_name)
                    if isinstance(result, list):
                        results[class_property] = result  # Store the result in the dictionary
                        total_pairs += len(result)  # Increment the count by the number of pairs found
                except ValueError as e:
                    # Log the error but continue processing the rest of the input
                    print(f"Error: {e}")
            else:
                print(f"Invalid input format for {class_property}. Use ClassName.property.")
    
    # Write the results to the output file in JSON format
    with open(output_file, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Print the total count of class-property pairs saved
    print(f"Total class-property pairs saved: {total_pairs}")

# Main execution
if __name__ == "__main__":
    idl_data_file = "/home/vagrant/BehavioralBiometricSA/idldata.json"  # Your path to idl_data.json
    input_file = "/home/vagrant/BehavioralBiometricSA/apis_collected/raw_apis/FP-tracer-sources.txt"  # Your input file with ClassName.property values
    output_file = "fp_sources.json"   # Output file for the results

    # Load the IDL data
    idl_data = load_data_from_file(idl_data_file)

    # Process the input file and generate the output
    process_properties(input_file, output_file, idl_data)
    print(f"Descendants and properties written to {output_file}")
