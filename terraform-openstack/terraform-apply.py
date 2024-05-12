import subprocess
import json

# Define the Terraform command to execute
terraform_command = ["sudo", "terraform", "apply"]
terraform_command2 = ["terraform", "output", "-json"]

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
        result = stdout.decode("utf-8")
        # Split the string by "Outputs:" and get the content after it
        output_needed = result.split("Outputs:")[2]
        print("OUTPUT NEEDED: ", output_needed)


    # Execute the Terraform command, redirecting stdout and stderr to pipes
    process = subprocess.Popen(terraform_command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    # Wait for the process to complete and get the output
    stdout, stderr = process.communicate()

    # Check if there were any errors
    if process.returncode != 0:
        print("Error executing Terraform command:")
        print(stderr.decode("utf-8"))
    else:
        print("Terraform command executed successfully:")
        result = stdout.decode("utf-8")
        #print("RESULT: ", result)
        terraform_dict = json.loads(result) # convert the result from json into a python format

        # Print the dictionary
        print("DICTIONARY: ", terraform_dict)

        

except Exception as e:
    print("An error occurred:", e)
