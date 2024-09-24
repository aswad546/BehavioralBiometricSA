import json

# Load the JSON data from the file
file_path = '/home/vagrant/BehavioralBiometricSA/idldata.json'
with open(file_path, 'r') as file:
    idl_data = json.load(file)

# Function to find all classes that inherit from a specific parent, directly or indirectly
def find_inheritors(idl_data, base_class):
    inheritors = set()
    
    def recursive_search(current_class):
        for class_name, class_info in idl_data.items():
            if class_info.get("parent") == current_class:
                if class_name not in inheritors:
                    inheritors.add(class_name)
                    recursive_search(class_name)
    
    recursive_search(base_class)
    return inheritors

# Find all classes that inherit from UIEvent
ui_event_inheritors = find_inheritors(idl_data, "UIEvent")
print(ui_event_inheritors)
