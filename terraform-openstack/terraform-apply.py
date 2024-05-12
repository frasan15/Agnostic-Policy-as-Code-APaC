import subprocess
import json

# Define the Terraform command to execute
terraform_command = ["sudo", "terraform", "apply"]
terraform_command2 = ["terraform", "output", "-json"]

# Run the Terraform command
try:
    # Execute the Terraform command, redirecting stdout and stderr to pipes
    process = subprocess.Popen(terraform_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    # Provide input to the process (e.g., "yes" to confirm actions)
    process.stdin.write(b"yes\n")
    process.stdin.flush()

    # Wait for the process to complete and get the output
    stdout, stderr = process.communicate()

    # Check if there were any errors
    if process.returncode != 0:
        print("Error executing Terraform command:")
        print(stderr.decode("utf-8"))
    else:
        print("Terraform command executed successfully:")
        result = stdout.decode("utf-8")
        # Split the string by "Outputs:" and get the content after it
        output_needed = result.split("Outputs:")[2]
        print("OUTPUT NEEDED: ", output_needed)


    # Execute the Terraform command, redirecting stdout and stderr to pipes
    process = subprocess.Popen(terraform_command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    # Wait for the process to complete and get the output
    stdout, stderr = process.communicate()

    # Check if there were any errors
    if process.returncode != 0:
        print("Error executing Terraform command:")
        print(stderr.decode("utf-8"))
    else:
        print("Terraform command executed successfully:")
        result = stdout.decode("utf-8")
        print("RESULT: ", result)
        terraform_dict = json.loads(result) # convert the result from json into a python format

        # Print the dictionary
        print("DICTIONARY: ", terraform_dict)

        # Create the generic JSON object and initialize the servers array, which will be containing all the information
        # needed for each server: name of the server and number of exposed ports
        final_results = {}
        final_results["servers"] = []
        final_results["subnets"] = []

        # The following operations allow to populate the servers array

        # Iterate over each server
        # Each object in Terraform-JSON output is wrapped onto an object, inside of this there are two arrays:
        # "type" and "value", value is the array containing the elements you are interested into.
        for server in terraform_dict['servers']['value']: 
            server_name = server['name']
            server_security_groups = server['security_groups'] # get the name of the security group implement in the current server
            
            # Initialize a list to store the exposed ports
            exposed_ports = []
            
            # Iterate over each security group of the server
            for security_group in server_security_groups: # security_group already represent the security group name
                
                # Find the corresponding security group in the list of security groups
                for sg in terraform_dict['security_groups']['value']:
                    if sg['name'] == security_group:
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

            # Fetch network name which the server belongs to
            network_name = server['network'][0]['name'] # N.B. in this way we are only analysing the first network the server belongs to, other networks are ignored
            
            subnets_list_ids = [] # initialize list of server's subnets

            # look for any correspondence comparing the network_name found in the server object and every network name in the networks object
            for network in terraform_dict['networks']['value']: 
                if network['name'] == network_name: 
                    network_id = network['id']
                    for subnet in network['subnets']: # fetch all the subnets belonging to such network
                        subnets_list_ids.append(subnet)
            
            # Create the result object for the current server, storing name, exposed ports and list of subnets ids
            result_object = {
                    'name': server_name,
                    'exposed_ports': exposed_ports,
                    'subnets': subnets_list_ids
            }

            # Append the result object to the final results list, in the servers array
            final_results["servers"].append(result_object)

            print(json.dumps(final_results, indent=4))

        

        

except Exception as e:
    print("An error occurred:", e)
