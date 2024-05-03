import ansible_runner
import json

r = ansible_runner.run(private_data_dir='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack', playbook='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml')

stdout_objects = []  # Initialize an empty list to store stdout objects

for each_host_event in r.events:
    if each_host_event['event'] == "runner_on_ok":
        if 'stdout' in each_host_event:
            stdout_value = each_host_event['stdout'].strip()  # Strip leading and trailing whitespace
            print("value:", stdout_value)
            if stdout_value:  # Check if stdout_value is not empty
                try:
                    stdout_objects.append(json.loads(stdout_value))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")

# Now stdout_objects contains the objects extracted from the stdout values

# Print each object in stdout_objects
for obj in stdout_objects:
    print("object: ", obj)
