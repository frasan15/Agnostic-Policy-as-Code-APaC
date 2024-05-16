# Program to convert yaml file to dictionary
import yaml
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
        return re.sub(r'\{{ | }}', '', value)
    else:
        return value

def check_key_exists(json_data, key):
        for index, obj in enumerate(json_data):
                if key in obj:
                        return True
        return False

indexes_servers = []
indexes_security_groups = []


# opening a file
try:
        with open('playbook.yml', 'r') as stream:
                # Converts yaml document to python object
                first = yaml.safe_load(stream)
        first = first[0]['tasks']
        second = []
        for item in first:
             second.append(process_value(item))

        #print("RESULT: ", json.dumps(second, indent=4))

        # Convert array of objects into an object of objects
        ansible_dictionary = {}
        ansible_dictionary['network'] = []
        ansible_dictionary['subnet'] = []
        ansible_dictionary['security_group'] = []
        ansible_dictionary['port'] = []
        ansible_dictionary['server'] = []
        ansible_dictionary['router'] = []
        ansible_dictionary['floating_ip'] = []

        for obj in second:
        # Get the second key of the object dynamically
                pre_key = list(obj.keys())[1]
                key = pre_key.split('.', 2)[2]

                ansible_dictionary[key].append(obj[pre_key])

        final_results = {}
        final_results["servers"] = []
        final_results["network_interfaces"] = []

        for server in ansible_dictionary['server']:
                server_name = server['name']
                server_security_groups = server['security_groups']

                # Initialize a list to store the exposed ports and the network interfaces of the current server
                exposed_ports = []
                network_interfaces = []
                
               # Iterate over each security group of the server
                for security_group_name in server_security_groups: # each item already represents the security group name
                
                        # Find the corresponding security group in the list of security groups
                        for sg in ansible_dictionary['security_group']:
                                if sg['name'] == security_group_name:
                                        security_group_rules = sg['security_group_rules'] # get the security group rules of the current security group
                                        
                                        # Iterate over each security group rule and port range min and max
                                        for rule in security_group_rules:
                                                port_range_min = rule['port_range_min']
                                                port_range_max = rule['port_range_max']
                                                
                                                # Add each port in the range to the exposed ports list; only if the port range is not None
                                                if port_range_max is not None and port_range_min is not None:
                                                        exposed_ports.extend(range(port_range_min, port_range_max + 1))

                # Remove duplicates and sort the exposed ports list
                exposed_ports = sorted(list(set(exposed_ports)))

                # Iterate through each network interface of the current server, and for each of them fetches the name
                # and the info whether it has a floating ip attached to it -> you do this by scanning the floating ip
                # array, looking for a match between the server_name associated to the current floating ip and the current
                # server being analysed -> if there's a match, then the nic attached to such a server has also a floating ip 
                for nic in server['nics']:
                        nic_name = nic['port-name']
                        network_interfaces.append(nic_name)

                        is_nic_public = False

                        for floating_ip in ansible_dictionary['floating_ip']:
                                if floating_ip['server'] == server_name:
                                        is_nic_public = True

                        nic_object = {
                               'name': nic_name,
                               'is_public': is_nic_public,
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

except yaml.YAMLError as e:
        print(e)
