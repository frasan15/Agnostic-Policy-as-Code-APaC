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

            for network in server['networks_advanced']:
                network_interfaces.append(network['name'].split('.', 2)[1])

            # Create the result object for the current server, storing name, exposed ports and list of subnets ids
            server_object = {
                    'name': server_name,
                    'exposed_ports': exposed_ports,
                    'network_interfaces': network_interfaces
            }
            final_results["servers"].append(server_object) 


    for network in terraform_dictionary['docker_network']:
        network_name = network['name'] 
        nic_object = {
        'name': network_name,
        'is_public': None
        }

        final_results['network_interfaces'].append(nic_object)



    print("FINAL JSON: ", json.dumps(final_results, indent=4))

except Exception as e:
    print("An error occurred:", e)