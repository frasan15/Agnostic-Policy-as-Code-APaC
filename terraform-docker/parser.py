import hcl2 # type: ignore
import json
import re
import os

# The following function is needed to remove the regular expression ${} from each value in the dictionary
def process_value(value):
    if isinstance(value, list):
        return [process_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: process_value(v) for k, v in value.items()}
    elif isinstance(value, str):
        return re.sub(r'\${|}', '', value)
    else:
        return value

try:
    # It reads the terraform file and it parses it onto a json file
    with open('main.tf', 'r') as file:
        first = hcl2.load(file)
    first = {key: process_value(value) for key, value in first.items()}
    first = first['resource']

    terraform_dictionary = {}
    terraform_dictionary['docker_image'] = []
    terraform_dictionary['docker_network'] = []
    terraform_dictionary['docker_container'] = []

    for item in first:
        key = list(item.keys())[0]
        nested_dict = item[key]
        terraform_dictionary[key].append(list(nested_dict.values())[0])
    
    print("JSON: ", json.dumps(terraform_dictionary, indent=4))

    final_results = {}
    final_results["servers"] = []
    final_results["network_interfaces"] = []

    for server in terraform_dictionary['docker_container']:
            server_name = server['name']

            # Initialize a list to store the exposed ports and the network interfaces of the current server
            exposed_ports = []
            network_interfaces = []

            for port in server['ports']:
                exposed_ports.append(port['internal'])
            
            exposed_ports = sorted(list(set(exposed_ports)))

            for port in server['ports']:
                network_interface_id = str(port['internal']) + ':' + str(port['external'])
                network_interfaces.append(network_interface_id)

                if port['ip'] == "0.0.0.0/0":
                    is_nic_public = True
                else:
                    is_nic_public = False

                nic_object = {
                    'name': network_interface_id,
                    'is_public': is_nic_public
                }
                final_results['network_interfaces'].append(nic_object)

            # Create the result object for the current server, storing name, exposed ports and list of subnets ids
            server_object = {
                    'name': server_name,
                    'exposed_ports': exposed_ports,
                    'network_interfaces': network_interfaces
            }
            final_results["servers"].append(server_object) 

    print("FINAL JSON: ", json.dumps(final_results, indent=4))

    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path for the JSON file
    json_file_path = os.path.join(current_dir, "result_object.json")

    # Write data to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(final_results, json_file, indent=4)

    print("JSON file has been generated and saved at:", json_file_path)

except Exception as e:
    print("An error occurred:", e)