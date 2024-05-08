import ansible_runner # type: ignore
import json
import re

r = ansible_runner.run(private_data_dir='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack', playbook='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml')

stdout_objects = []  # Initialize an empty list to store stdout objects

for each_host_event in r.events:
    if each_host_event['event'] == "runner_on_ok": # take only events marked with "runner_on_ok" since the information about network and security group are stored in such events
        if 'stdout' in each_host_event: # check if such event has got the stdout field
            stdout_value = each_host_event['stdout']  # take the value corresponding to the stdout field
            #print("value:", stdout_value)
            # Remove ANSI escape codes from the string -> this escape code makes the json to look green and modify the length of the string causing a lot of issues
            clean_stdout_value = re.sub(r'\x1b\[[0-9;]*m', '', stdout_value)
            #print("Cleaned value: ", clean_stdout_value)
            #print(clean_stdout_value.startswith("ok: [localhost]"))
            
            if clean_stdout_value.startswith("ok: [localhost] =>"):  # These are the only values where the information about network and security group are stored
                # Extract the object, by removing the 'ok: [localhost] =>' part and keep both the first '{' and the last '}' since they are needed to represent a json object
                # The characters '\n' and ' ' are needed as well to represent the json object (you see them with repr())
                object_start_index = clean_stdout_value.find("{")
                object_str = clean_stdout_value[object_start_index:]
                print("json formatted: ", object_str) # here you can see that the object is no longer green
                stdout_objects.append(json.loads(object_str))


# Print each object in stdout_objects
#for obj in stdout_objects:
 #   print("object: ", obj)


result_dict = {}
# Iterate over each object in stdout_objects
for obj in stdout_objects:
    # Check if the object contains a 'msg' key and 'failed' key within the 'msg' dictionary
    if 'msg' in obj and 'failed' in obj['msg']:
        msg_keys = list(obj['msg'].keys())  # Get all keys in the 'msg' dictionary
        failed_index = msg_keys.index('failed')  # Find the index of 'failed' key
        if failed_index < len(msg_keys) - 1:  # Ensure there's a key after 'failed'
            next_key = msg_keys[failed_index + 1]  # Get the key following 'failed' -> we do this since the key after the key 'failed' represent the information related to the object itself. DRAWBACK: this implementation is extremely hard-coded, so not really good.
            result_dict[next_key] = obj['msg'][next_key]  # Store the entire object as the value
            # take in mind that obj['msg'] is no longer a json object
            # this is useful since we still need to process this object in Python
            # however, we will need to convert into a json before creating the generic json file
            
# Print the resulting dictionary
print(result_dict)


# Initialize a list to store the final results
final_results = []

# Iterate over each server
for server in result_dict['servers']:
    server_name = server['name']
    server_security_groups = server['security_groups']
    
    # Initialize a list to store the exposed ports
    exposed_ports = []
    
    # Iterate over each security group of the server
    for security_group in server_security_groups:
        security_group_name = security_group['name']
        
        # Find the corresponding security group in the list of security groups
        for sg in result_dict['security_groups']:
            if sg['name'] == security_group_name:
                security_group_rules = sg['security_group_rules']
                
                # Iterate over each security group rule
                for rule in security_group_rules:
                    port_range_min = rule['port_range_min']
                    port_range_max = rule['port_range_max']
                    
                    # Add each port in the range to the exposed ports list
                    exposed_ports.extend(range(port_range_min, port_range_max + 1))
    
    # Remove duplicates and sort the exposed ports list
    exposed_ports = sorted(list(set(exposed_ports)))
    
    # Create the result object for the current server
    result_object = {
        'name': server_name,
        'exposed_ports': exposed_ports
    }
    
    # Append the result object to the final results list
    final_results.append(result_object)

# Print the final results
print(json.dumps(final_results, indent=4))