from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible import context

# Set the path to your playbook
playbook_path = '/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml'

# Initialize Ansible context
context.CLIARGS = {'syntax': False}

# Initialize Ansible context
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources='localhost')
variable_manager = VariableManager(loader=loader, inventory=inventory)

# Create a playbook executor
pbex = PlaybookExecutor(
    playbooks=[playbook_path],
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords={}
)

# Run the playbook
results = pbex.run()

# Access the registered variables
network_details = variable_manager.get_vars()['network_details']
security_group_details = variable_manager.get_vars()['security_group_details']

# Print the network details
print("Network details:")
print(network_details)

# Print the security group details
print("Security group details:")
print(security_group_details)
