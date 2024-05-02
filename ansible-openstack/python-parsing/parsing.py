import yaml

# Load YAML data from a file
with open('/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml', "r") as file:
    data = yaml.safe_load(file)

# Now 'data' contains the parsed YAML data
print(data)