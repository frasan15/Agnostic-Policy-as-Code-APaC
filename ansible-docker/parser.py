import yaml
import json
import os

try:
    with open('playbook.yml', 'r') as stream:
        first = yaml.safe_load(stream)
    first = first[0]['tasks']

    # Convert array of objects into an object of objects
    ansible_dictionary = {}
    ansible_dictionary['docker_image'] = []
    ansible_dictionary['docker_network'] = []
    ansible_dictionary['docker_container'] = []

    for obj in first:
    # Get the second key of the object dynamically
        pre_key = list(obj.keys())[1]
        key = pre_key.split('.', 2)[2]

        ansible_dictionary[key].append(obj[pre_key])
    
    print("RESULT: ", json.dumps(ansible_dictionary, indent=4))

    final_results = {}
    final_results["servers"] = []
    final_results["network_interfaces"] = []

    for server in ansible_dictionary['docker_container']:
        server_name = server['name']
        ports_mapping = server['ports']

        # Initialize a list to store the exposed ports and the network interfaces of the current server
        exposed_ports = []
        network_interfaces = []

        # Iterate over each security group of the server
        for port in ports_mapping: # each item already represents the security group name
                network_interfaces.append(port.split(':', 1)[1]) # we use host_port:container_port as key for the network interface

                port_host_interface = port.split(':', 2)[0]
                if port_host_interface == "0.0.0.0":
                     is_nic_public = True
                else:
                     is_nic_public= False

                nic_object = {
                    'name': port.split(':', 1)[1],
                    'is_public': is_nic_public
                }
                final_results['network_interfaces'].append(nic_object)

                port = port.split(':', 2)[2]
                exposed_ports.append(int(port)) # here we only need the container exposed port

        # Create the result object for the current server, storing name, exposed ports and list of subnets ids
        server_object = {
                'name': server_name,
                'exposed_ports': exposed_ports,
                'server_network_interfaces': network_interfaces
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

except yaml.YAMLError as e:
        print(e)