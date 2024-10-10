import json

def find_all_properties(event_name):
    # Load the JSON data
    with open("/home/vagrant/BehavioralBiometricSA/webidl_apis_with_parents.json") as f:
        data = json.load(f)

    # Collect all properties, including those from parents
    def collect_properties(interface):
        properties = set()
        while interface and interface in data:
            # Add the properties of the current interface
            if "properties" in data[interface]:
                properties.update(data[interface]["properties"])
            # Move to the parent interface
            interface = data[interface].get("parent")
        return properties

    # Return the collected properties for the given event/interface
    return list(collect_properties(event_name))

# Example usage:
event_properties = find_all_properties("DeviceOrientationEvent")
for x in event_properties:
    print(f"DeviceOrientationEvent.{x}")

