# The following code is able to run the Ansible Playbook from this Python script

import ansible_runner
r = ansible_runner.run(private_data_dir='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack', playbook='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml')

stdout_list = []  # Initialize an empty list to store stdout values
for each_host_event in r.events:
    if each_host_event['event'] == "runner_on_ok":
        if 'stdout' in each_host_event:
            stdout_list.append(each_host_event['stdout'])

# Now stdout_list contains all stdout values corresponding to events with 'runner_on_ok'

# Print each value in stdout_list
for stdout_value in stdout_list:
    print(stdout_value)