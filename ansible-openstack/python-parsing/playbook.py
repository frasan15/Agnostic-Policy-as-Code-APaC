from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

# Set the path to your playbook
playbook_path = '/home/ubuntu/Verification-and-Validation-of-IaC/ansible-openstack/playbook.yml'

# Initialize Ansible context
context.CLIARGS = {}

# You can then set specific command-line arguments as needed
# For example, to set the verbosity level to 2:
context.CLIARGS['verbosity'] = 2

# Load data
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources=['localhost'])
variable_manager = VariableManager(loader=loader, inventory=inventory)

# Create a playbook executor
pbex = PlaybookExecutor(
    playbooks=[playbook_path],
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords={},
)

# Run the playbook
results = pbex.run()

# Print the results
print(results)
