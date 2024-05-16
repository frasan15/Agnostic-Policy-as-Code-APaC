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

    #terraform_dictionary = {key: process_value(value) for key, value in terraform_dictionary.items()}

    first = first['resource']

    network = "openstack_networking_network_v2"
    subnet = "openstack_networking_subnet_v2"
    security_group = "openstack_networking_secgroup_v2"
    port = "openstack_networking_port_v2" # network interfaces
    server = "openstack_compute_instance_v2"
    router = "openstack_networking_router_v2"
    router_interface = "openstack_networking_router_interface_v2"
    floating_ip = "openstack_networking_floatingip_v2"

    terraform_dictionary = {}
    terraform_dictionary[network] = []
    terraform_dictionary[subnet] = []
    terraform_dictionary[security_group] = [] # here there's both resources from openstack_networking_secgroup_v2 and openstack_networking_secgroup_rule_v2
    terraform_dictionary[port] = []
    terraform_dictionary[server] = []
    terraform_dictionary[router] = []
    terraform_dictionary[router_interface] = []
    terraform_dictionary[floating_ip] = []


    # Temporary storage for secgroup rules -> this step is needed to store the resources from openstack_networking_secgroup_rule_v2 into openstack_networking_secgroup_v2
    secgroup_rules = {}

    for item in first:
        key = list(item.keys())[0]
        if key == "openstack_networking_secgroup_rule_v2":
            nested_key = list(item[key].keys())[0]
            secgroup_id = (item[key][nested_key]["security_group_id"]).split('.', 2)[1]
            if secgroup_id not in secgroup_rules:
                secgroup_rules[secgroup_id] = []
            secgroup_rules[secgroup_id].append(item[key][nested_key])
        else:
            nested_dict = item[key]
            terraform_dictionary[key].append(list(nested_dict.values())[0])

    # Append secgroup rules to corresponding secgroup objects
    for secgroup_name, rules in secgroup_rules.items():
        for secgroup in terraform_dictionary[security_group]:
            if secgroup['name'] == secgroup_name:
                if 'rules' not in secgroup:
                    secgroup['rules'] = []
                secgroup['rules'].extend(rules)

    json_string = json.dumps(terraform_dictionary, indent=4)
    #print(json_string)

    final_results = {}
    final_results["servers"] = []
    final_results["network_interfaces"] = []

    for server in terraform_dictionary[server]:
            server_name = server['name']
            server_security_groups = server['security_groups']

            for item in server_security_groups: # every server_security_groups is stored as "openstack_networking_secgroup_v2.secgroup_2.name" so we need to extract the name
                item = (item).split('.', 2)[1]

            # Initialize a list to store the exposed ports and the network interfaces of the current server
            exposed_ports = []
            network_interfaces = []
            
            # Iterate over each security group of the server
            for security_group_name in server_security_groups: # each item already represents the security group name
                    # Find the corresponding security group in the list of security groups
                    for sg in terraform_dictionary[security_group]:
                            if sg['name'] == (security_group_name).split('.', 2)[1]:
                                    security_group_rules = sg['rules'] # get the security group rules of the current security group
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
            for nic in server['network']:
                    nic_name = nic['port']
                    nic_name = (nic_name).split('.', 2)[1]
                    network_interfaces.append(nic_name)

                    is_nic_public = False

                    for item in terraform_dictionary[floating_ip]:
                            
                            if (item['port_id']).split('.', 2)[1] == nic_name:
                                    is_nic_public = True

                    nic_object = {
                            'name': nic_name,
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
