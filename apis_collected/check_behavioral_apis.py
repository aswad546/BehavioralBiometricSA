import re
import json
# Script to find all behavioral APIS in each script from the logs in this directory
def getValidApis():
    std_api = []
    with open("/home/vagrant/BehavioralBiometricSA/idldata.json") as f:
        data = json.load(f)

    for i in data:
        if data[str(i)] is not None:
            if "members" in data[str(i)]:
                for ele in data[str(i)]["members"]:
                    std_api.append(str(i) + "." + str(ele))
                if "parent" in data[str(i)]:
                    curr = data[str(i)]['parent']
                    while (curr != None):
                        if "members" in data[str(curr)]:
                            for api in data[str(curr)]["members"]:
                                std_api.append(str(i)+"."+str(api))
                        if "parent" in data[str(curr)]:
                            curr = data[str(curr)]['parent']
                        else:
                            break
            else:
                for ele in data[str(i)].values():
                    std_api.append(str(i) + "." + str(ele))
    return std_api

# Step 1: Read the input from a file
input_file_path = './Sardine.apis'  # Replace with the actual path to your input file

dict1 = {}
std_api = getValidApis()
for i in std_api:
    dict1[i] = True

with open(input_file_path, 'r') as file:
    output = file.read()  # Read the entire content of the file into a string

# Step 2: Remove extra characters and split the string into a list
cleaned_output = re.sub(r'[{}"]', '', output)  # Remove curly braces and extra quotes
elements = cleaned_output.split(',')

# Step 3: Filter out elements that contain the word 'event'
filtered_elements = [elem for elem in elements if 'event' in elem.split('.')[0].lower() or 'touch' in elem.split('.')[0].lower()]

# Step 4: Remove duplicates by converting the list to a set, then back to a list
unique_elements = list(set(filtered_elements))

# Step 5: Sort the unique elements
sorted_elements = sorted(unique_elements)

# Step 6: Print the output
for elem in sorted_elements:
    print(elem)
