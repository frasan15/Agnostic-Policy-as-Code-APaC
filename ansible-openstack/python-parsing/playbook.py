import ansible_runner
import json

r = ansible_runner.run(private_data_dir='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack', playbook='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml')

stdout_objects = []  # Initialize an empty list to store stdout objects

for each_host_event in r.events:
    if each_host_event['event'] == "runner_on_ok":
        if 'stdout' in each_host_event:
            stdout_value = each_host_event['stdout']
            print("value:", stdout_value)
            
            # Extracting the JSON part
            json_start_index = stdout_value.find('{')
            json_end_index = stdout_value.rfind('}') + 1
            json_str = stdout_value[json_start_index:json_end_index]

            try:
                stdout_objects.append(json.loads(json_str))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

# Now stdout_objects contains the objects extracted from the stdout values

# Print each object in stdout_objects
for obj in stdout_objects:
    print("object: ", obj)
