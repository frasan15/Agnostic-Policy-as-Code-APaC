import hcl2
import json
import re

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
    
# Given a key, this function retrieves the indexes where json_data[index] = "key":{...}
# It's needed to get the indexes where json_data[index] = "openstack_networking_secgroup_v2" or json_data[index] = "openstack_networking_secgroup_rule_v2"
def get_indexes(json_data, key):
    for index, obj in enumerate(json_data):
        if key in obj and key == security_group_keyword:
            indexes_sg.append(index)
        elif key in obj and key == security_group_rules_keyword:
            indexes_sg_rules.append(index)

# It checks whether a key exists before attempting to access to its value
# In particular, this is needed to correctly access to terraform_dictionary['resource'][index][security_group_keyword][security_group_keyword_2] and retrieve the name of the security group
def check_key_exists(json_data, key):
    for index, obj in enumerate(json_data):
        if key in obj:
            return True
    return False

# The following are well-known keywords from Terraform and are needed to access the various resources
server_keyword = "openstack_compute_instance_v2"
security_group_keyword = "openstack_networking_secgroup_v2"
security_group_rules_keyword = "openstack_networking_secgroup_rule_v2"

servers_info = [] # array of objects, where each object will be representing a different server

indexes_sg = [] # array containing the indexes where terraform_dictionary['resource'][index] == "openstack_networking_secgroup_v2"
indexes_sg_rules = [] # array containing the indexes where terraform_dictionary['resource'][index] == "openstack_networking_secgroup_rule_v2"

# It reads the terraform file and it parses it onto a json file
with open('main.tf', 'r') as file:
    terraform_dictionary = hcl2.load(file)

terraform_dictionary = {key: process_value(value) for key, value in terraform_dictionary.items()}

json_string = json.dumps(terraform_dictionary, indent=4)
print(json_string)

try:
    # Create the generic JSON object and initialize the servers array, which will be containing all the information
    # needed for each server: name of the server, number of exposed ports and network where 
    final_results = {}
    final_results["servers"] = []
    final_results["networks"] = []
    final_results["ports"] = []

    # Fetching server info
    for index, resource in enumerate(terraform_dictionary['resource']): # terraform_dictionary['resource'] contains each resource info
        if server_keyword in resource:
            servers_info.append(resource[server_keyword])

    for server in servers_info:
        for s in server:
            key_current_server = s # the key wrapping the current server info (e.g., server_1, server_2)
        #print("CURRENT SERVER: ", server[key_current_server])
        server_name = server[key_current_server]['name']
        server_security_groups = server[key_current_server]['security_groups'] # get the name of the security groups implemented in the current server
        
        # Initialize a list to store the exposed ports
        exposed_ports = []
        #print("NAME: ", server_name)
        #print("SECGROUPS: ", server_security_groups)

        # Iterate over each security group of the server
        for security_group in server_security_groups: # security_group already represent the security group name

            # Split the string by the first '.' character, since here it's placed the keywords through which we can access the current security group; 
            # We would need to combine such a keyword with the generic security group keyword
            # For instance, from openstack_networking_secgroup_v2.secgroup_2.name this fetches secgroup_2
            parts = security_group.split('.', 2)
            security_group_keyword_2 = parts[1]

            get_indexes(terraform_dictionary['resource'], security_group_keyword) # get the indexes where terraform_dictionary['resource'][index] == security_group_keyword
            # For each index we check whether terraform_dictionary['resource'][index][security_group_keyword][security_group_keyword_2] exists
            # This is needed since terraform_dictionary['resource'][index][security_group_keyword] contains also another key which refers to the other security group
            for index in indexes_sg:
                index_exists = check_key_exists(terraform_dictionary['resource'][index][security_group_keyword], security_group_keyword_2)
                if index_exists:
                    security_group_name = terraform_dictionary['resource'][index][security_group_keyword][security_group_keyword_2]['name']
                    #print("FIRST: ", next(iter(terraform_dictionary['resource'][index][security_group_keyword].keys()), None)) # read the key refering to the key name of the security group rule
                    sg_keyname = next(iter(terraform_dictionary['resource'][index][security_group_keyword].keys()), None) # this is either secgroup_1 or secgroup_2

            get_indexes(terraform_dictionary['resource'], security_group_rules_keyword) # get the indexes where terraform_dictionary['resource'][index] == security_group_rules_keyword
            for index1 in indexes_sg_rules:
                for item in terraform_dictionary['resource'][index1][security_group_rules_keyword]:
                    #print("ITEM: ", item)
                    # The following line finds the security group id which is refered to into the current security group rule
                    # Once it is found, it extracts the ports exposed 
                    if terraform_dictionary['resource'][index1][security_group_rules_keyword][item]['security_group_id'] == f'{security_group_keyword}.{sg_keyname}.id':
                        # Iterate over each security group rule and port range min and max
                        port_range_min = terraform_dictionary['resource'][index1][security_group_rules_keyword][item]['port_range_min']
                        port_range_max = terraform_dictionary['resource'][index1][security_group_rules_keyword][item]['port_range_max']
                        
                        # Add each port in the range to the exposed ports list; only if the port range is not None
                        if port_range_max is not None and port_range_min is not None:
                            exposed_ports.extend(range(port_range_min, port_range_max + 1))
            
            # Reset indexes arrays for the next server
            indexes_sg = []
            indexes_sg_rules = []
        
        # Remove duplicates and sort the exposed ports list
        exposed_ports = sorted(list(set(exposed_ports)))

        # Create the result object for the current server, storing name, exposed ports and list of subnets ids
        result_object = {
                'name': server_name,
                'exposed_ports': exposed_ports
        }

        print("RESSS: ", result_object)


            

except Exception as e:
    print("An error occurred:", e)
