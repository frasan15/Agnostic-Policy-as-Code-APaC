from python_terraform import Terraform

# Initialize Terraform
tf = Terraform(working_dir='/home/ubuntu/Verification-and-Validation-of-IaC/terraform-openstack')

# Run 'terraform init'
init_result = tf.init()

# Check if 'terraform init' was successful
if init_result[0] != 0:
    print("Error initializing Terraform:")
    print(init_result[1])
    exit(1)

# Run 'terraform plan'
plan_result = tf.plan()

# Check if 'terraform plan' was successful
if plan_result[0] != 0:
    print("Error running Terraform plan:")
    print(plan_result[1])
    exit(1)

# Parse the plan output
plan_output = tf.show()

# Print the plan output
print("Terraform Plan:")
print(plan_output)

# Apply the plan
apply_result = tf.apply(skip_plan=True)

# Check if 'terraform apply' was successful
if apply_result[0] != 0:
    print("Error applying Terraform plan:")
    print(apply_result[1])
    exit(1)

# Output successful message
print("Terraform apply successful.")
