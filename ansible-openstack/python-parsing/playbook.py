import ansible_runner
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
                # Extract the object and remove the first '{' and the last '}'
                object_start_index = clean_stdout_value.find("{")
                object_end_index = clean_stdout_value.rfind("}")
                object_str = clean_stdout_value[object_start_index+1:object_end_index].strip()
                print("json formatted: ", object_str) # here you can see that the object is no longer green
                print("Repr cleaned value ", repr(object_str))
                stdout_objects.append(json.loads(object_str)) # this line doesn't work yet, since there's still some issue with converting the string into json


# Print each object in stdout_objects
for obj in stdout_objects:
    print("object: ", obj)
