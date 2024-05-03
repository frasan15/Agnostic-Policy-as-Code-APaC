import ansible_runner
import json

r = ansible_runner.run(private_data_dir='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack', playbook='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml')

stdout_objects = []  # Initialize an empty list to store stdout objects

for each_host_event in r.events:
    if each_host_event['event'] == "runner_on_ok":
        if 'stdout' in each_host_event:
            stdout_value = each_host_event['stdout'].strip()  # Strip leading and trailing whitespace
            print("value:", stdout_value)
            print(stdout_value.find("2"))
            print(stdout_value.startswith("b[0;32mok: [localhost]"))
            if stdout_value.startswith("ok: [localhost]"):  # Remove space after ":"
                # Extract the object and remove the last '}'
                object_start_index = stdout_value.find("{")
                object_end_index = stdout_value.rfind("}")
                object_str = stdout_value[object_start_index:object_end_index]
                stdout_objects.append(json.loads(object_str))

# Now stdout_objects contains the objects extracted from the second kind of stdout values

# Print each object in stdout_objects
for obj in stdout_objects:
    print("object: ", obj)
