# Program to convert yaml file to dictionary
import yaml
import json
import re

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
with open('playbook.yml', 'r') as stream:
    try:
        # Converts yaml document to python object
        first = yaml.safe_load(stream)
        first = first[0]['tasks']
        second = []
        for item in first:
             second.append(process_value(item))

        print("RESSS: ", json.dumps(second, indent=4))

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

        print("NEWWWWWW: ", json.dumps(ansible_dictionary, indent=4))

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

                for nic in server['nics']:
                      network_interfaces.append(nic['port-name'])
                
                        # Create the result object for the current server, storing name, exposed ports and list of subnets ids
                server_object = {
                        'name': server_name,
                        'exposed_ports': exposed_ports,
                        'network_interfaces': network_interfaces
                }

                final_results["servers"].append(server_object)

                print("FINAL JSON: ", json.dumps(final_results, indent=4))


        


    except yaml.YAMLError as e:
            print(e)
