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
        result = stdout.decode("utf-8")
        # Split the string by "Outputs:" and get the content after it
        #outputs_section = result.split("Outputs:")[0]
        #second_o = result.split("Outputs:")[1]
        mine = result.split("Outputs:")[2]
        #print("RESULT: ", result)
        #print("FIRST: ", outputs_section)
        #print("SECOND: ", second_o)
        print("MINE: ", mine)

        # Remove unnecessary characters
        terraform_output = mine.replace(" = ", ":")
        terraform_output = terraform_output.replace("toset([])", "[]")
        terraform_output = terraform_output.replace("tolist([])", "[]")
        terraform_output = terraform_output.replace("tomap({})", "{}")
        terraform_output = terraform_output.replace("tostring(null)", "null")
        terraform_output = terraform_output.replace("tobool(null)", "null")
        terraform_output = terraform_output.replace("/* of string */", "")
        terraform_output = terraform_output.replace("false", "False")
        terraform_output = terraform_output.replace("true", "True")
        terraform_output = terraform_output.replace("network_info", "'network_info'")
        terraform_output = terraform_output.replace("security_group_info", "'security_group_info'")
        terraform_output = terraform_output.replace("server_info", "'server_info'")
        terraform_output = terraform_output.replace("server_info_2", "'server_info_2'")
        terraform_output = terraform_output.replace("server_instance_ids", "'server_instance_ids'")
        terraform_output = terraform_output.replace("subnet_info", "'subnet_info'")

        # Replace '=' with ':' and wrap keys in double quotes
        terraform_output = terraform_output.replace("\n", ",\n").replace(" = ", ":")
        terraform_output = "{" + terraform_output + "}"

        print("TATATATT: ", terraform_output)

        # Split the data into lines
        #lines = terraform_output.split('\n')

        # Remove trailing comma for the first three lines
        #modified_lines = [line.rstrip(',') if index < 3 else line for index, line in enumerate(lines)]

        # Join the modified lines back into a string
        #modified_data = '\n'.join(modified_lines)

        #print("MODIFIED: ", modified_data)

        # Convert string to dictionary
        terraform_dict = eval(terraform_output)

        # Print the dictionary
        print("DICTIONARY: ", terraform_dict)

except Exception as e:
    print("An error occurred:", e)
