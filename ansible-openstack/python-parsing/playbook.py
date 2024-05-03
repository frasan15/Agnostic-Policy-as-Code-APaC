# The following code is able to run the Ansible Playbook from this Python script

import ansible_runner
r = ansible_runner.run(private_data_dir='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack', playbook='/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml')
print("this is the format: {}: {}".format(r.status, r.rc))
# successful: 0
for each_host_event in r.events:
    print(each_host_event['uuid'])
print("Final status:")
print(r.stdout)