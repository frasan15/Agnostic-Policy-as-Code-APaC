# Program to convert yaml or hcl infrastructure code into a generic json file
import hcl2 # type: ignore
import yaml
import json
import re
import os
import argparse

# The following lines are needed to handle the CLI parameters, which will be used (at the end of this file) 
# to detect which version of the parser needs to be executed

# Initialize the parser
parser = argparse.ArgumentParser(description="Proof of Concept's Parser")

# Add arguments
parser.add_argument('--tool', type=str, help='Infrastructure as Code tool')
parser.add_argument('--provider', type=str, help='Infrastructure Provider')

# The following lines of code are needed to specify the right path where each infrastructure code file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Paths for the infrastructure code for each of the four configurations
ansible_openstack_example = os.path.join(parent_dir, "infrastructure-provisioning-and-deployment-examples/ansible-openstack/playbook.yml")
ansible_docker_example = os.path.join(parent_dir, "infrastructure-provisioning-and-deployment-examples/ansible-docker/playbook.yml")
terraform_openstack_example = os.path.join(parent_dir, "infrastructure-provisioning-and-deployment-examples/terraform-openstack/main.tf")
terraform_docker_example = os.path.join(parent_dir, "infrastructure-provisioning-and-deployment-examples/terraform-docker/main.tf")

# The following will be the json object representing the infrastructure using high-level keywords
final_results = {}
final_results["servers"] = []
final_results["network_interfaces"] = []

# The following function is needed to remove the regular expression ${} from each value in the dictionary,
# when dealing with Ansible playbooks
def process_value_ansible(value):
        if isinstance(value, list):
                return [process_value_ansible(v) for v in value]
        elif isinstance(value, dict):
                return {k: process_value_ansible(v) for k, v in value.items()}
        elif isinstance(value, str):
                return re.sub(r'\{{ | }}', '', value)
        else:
                return value
        
# The following function is needed to remove the regular expression ${} from each value in the dictionary,
# when dealing with Terraform files
def process_value_terraform(value):
        if isinstance(value, list):
                return [process_value_terraform(v) for v in value]
        elif isinstance(value, dict):
                return {k: process_value_terraform(v) for k, v in value.items()}
        elif isinstance(value, str):
                return re.sub(r'\${|}', '', value)
        else:
                return value

try:
        def ansible_openstack():
                # opening a file
                with open(ansible_openstack_example, 'r') as stream:
                        # Converts yaml document to python object
                        first = yaml.safe_load(stream)
                first = first[0]['tasks']
                second = []
                for item in first:
                        second.append(process_value_ansible(item))

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
                                                # get the security group rules of the current security group
                                                security_group_rules = sg['security_group_rules'] 
                                                
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
                        # server being analysed -> if there is a match, then the nic attached to such a server has also a floating ip 
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
                                'server_network_interfaces': network_interfaces
                        }

                        final_results["servers"].append(server_object)

        
        def ansible_docker():
                with open(ansible_docker_example, 'r') as stream:
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

                for server in ansible_dictionary['docker_container']:
                        server_name = server['name']
                        ports_mapping = server['ports']

                        # Initialize a list to store the exposed ports and the network interfaces of the current server
                        exposed_ports = []
                        network_interfaces = []

                        # Iterate over each security group of the server
                        # Each item already represents the security group name
                        for port in ports_mapping: 
                                # We use host_port:container_port as key for the network interface
                                network_interfaces.append(port.split(':', 1)[1]) 

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
                                # Here we only need the container exposed port
                                exposed_ports.append(int(port)) 

                        # Create the result object for the current server, storing name, exposed ports and list of subnets ids
                        server_object = {
                                'name': server_name,
                                'exposed_ports': exposed_ports,
                                'server_network_interfaces': network_interfaces
                        }

                        final_results["servers"].append(server_object)

        
        def terraform_openstack():
                # It reads the terraform file and it parses it into a json file
                with open(terraform_openstack_example, 'r') as file:
                        first = hcl2.load(file)
                        first = {key: process_value_terraform(value) for key, value in first.items()}

                first = first['resource']
                network = "openstack_networking_network_v2"
                subnet = "openstack_networking_subnet_v2"
                security_group = "openstack_networking_secgroup_v2"
                # network interfaces
                port = "openstack_networking_port_v2" 
                server = "openstack_compute_instance_v2"
                router = "openstack_networking_router_v2"
                router_interface = "openstack_networking_router_interface_v2"
                floating_ip = "openstack_networking_floatingip_v2"

                terraform_dictionary = {}
                terraform_dictionary[network] = []
                terraform_dictionary[subnet] = []
                # here there is both resources from openstack_networking_secgroup_v2 and openstack_networking_secgroup_rule_v2
                terraform_dictionary[security_group] = [] 
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

                for server in terraform_dictionary[server]:
                        server_name = server['name']
                        server_security_groups = server['security_groups']

                        # Every server_security_groups is stored as "openstack_networking_secgroup_v2.secgroup_2.name" so we need to extract the name
                        for item in server_security_groups: 
                                item = (item).split('.', 2)[1]

                        # Initialize a list to store the exposed ports and the network interfaces of the current server
                        exposed_ports = []
                        network_interfaces = []
                        
                        # Iterate over each security group of the server
                        # Each item already represents the security group name
                        for security_group_name in server_security_groups: 
                                # Find the corresponding security group in the list of security groups
                                for sg in terraform_dictionary[security_group]:
                                        if sg['name'] == (security_group_name).split('.', 2)[1]:
                                                # Get the security group rules of the current security group
                                                security_group_rules = sg['rules'] 
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
                        # server being analysed -> if there is a match, then the nic attached to such a server has also a floating ip 
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
                                'server_network_interfaces': network_interfaces
                        }

                        final_results["servers"].append(server_object)            


        def terraform_docker():
                # It reads the terraform file and it parses it onto a json file
                with open(terraform_docker_example, 'r') as file:
                        first = hcl2.load(file)
                first = {key: process_value_terraform(value) for key, value in first.items()}
                first = first['resource']

                terraform_dictionary = {}
                terraform_dictionary['docker_image'] = []
                terraform_dictionary['docker_network'] = []
                terraform_dictionary['docker_container'] = []

                for item in first:
                        key = list(item.keys())[0]
                        nested_dict = item[key]
                        terraform_dictionary[key].append(list(nested_dict.values())[0])

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
                                'server_network_interfaces': network_interfaces
                        }
                        
                        final_results["servers"].append(server_object) 


        # Parse the arguments. The arguments can be retrieve by args.tool or args.provider
        args = parser.parse_args()
        # run the proper parser according to the IaC tool and the infrastructure provider
        if args.tool == "ansible" and args.provider == "openstack":
                ansible_openstack()
        elif args.tool == "ansible" and args.provider == "docker":
                ansible_docker()
        elif args.tool == "terraform" and args.provider == "openstack":
                terraform_openstack()
        elif args.tool == "terraform" and args.provider == "docker":
                terraform_docker()
        else:
                raise Exception("Infrastructure as Code tool or Infrastructure Provider not supported")

        print("FINAL JSON: ", json.dumps(final_results, indent=4))
        # The following are the operations needed to write the json file on the current folder
        # Define the path for the JSON file
        json_file_path = os.path.join(current_dir, "network_infrastructure.json")
        # Write data to the JSON file
        with open(json_file_path, 'w') as json_file:
                json.dump(final_results, json_file, indent=4)
        print("JSON file has been generated and saved at:", json_file_path)

except Exception as e:
        print(e)