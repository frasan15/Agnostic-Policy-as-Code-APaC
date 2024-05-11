import subprocess

# Define the Terraform command to execute
terraform_command = ["sudo", "terraform", "apply"]

# Run the Terraform command
try:
    # Execute the Terraform command, redirecting stdout and stderr to pipes
    process = subprocess.Popen(terraform_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    # Provide input to the process (e.g., "yes" to confirm actions)
    process.stdin.write(b"yes\n")
    process.stdin.flush()

    # Wait for the process to complete and get the output
    stdout, stderr = process.communicate()

    # Check if there were any errors
    if process.returncode != 0:
        print("Error executing Terraform command:")
        print(stderr.decode("utf-8"))
    else:
        print("Terraform command executed successfully:")
        print(stdout.decode("utf-8"))

except Exception as e:
    print("An error occurred:", e)
