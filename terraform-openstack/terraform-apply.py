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

        # Remove unnecessary (and problematic) characters
        terraform_output = mine.replace(" = ", ":")
        terraform_output = terraform_output.replace("tomap({})", "{}")
        terraform_output = terraform_output.replace("tostring(null)", "None")
        terraform_output = terraform_output.replace("tobool(null)", "None")
        terraform_output = terraform_output.replace("null", "None")
        terraform_output = terraform_output.replace("/* of string */", "")
        terraform_output = terraform_output.replace("false", "False")
        terraform_output = terraform_output.replace("true", "True")
        terraform_output = terraform_output.replace('"True"', "True")
        terraform_output = terraform_output.replace('"False"', "False")
        terraform_output = terraform_output.replace("])", "]")
        terraform_output = terraform_output.replace('",', '"')

        # You need to change the following everytime you change the infrastructure
        terraform_output = terraform_output.replace("network_info", '"network_info"')
        terraform_output = terraform_output.replace("security_group_info", '"security_group_info"')
        terraform_output = terraform_output.replace("server_info_2", '"server_info_2"')
        terraform_output = terraform_output.replace("server_info:", '"server_info":')
        terraform_output = terraform_output.replace("server_instance_ids", '"server_instance_ids"')
        terraform_output = terraform_output.replace("subnet_info", '"subnet_info"')

        # Split the data into lines
        lines = terraform_output.split('\n')

        # Initialize a list to store modified lines
        modified_lines = []

        # Iterate through the lines
        for line in lines:
            # Flag to determine whether the current lines needs a comma at the end of itself
            comma_needed = True

            # Remove unnecessary characters
            if "tolist(" or "toset(" in line:
                 line = line.replace("tolist([", "[")
                 line = line.replace("toset([", "[")
                 line = line.replace("tolist(", "")
                 line = line.replace("toset(", "")
                 line = line.replace("])", "]")
                 line = line.replace(")", "")

            if line.strip().endswith('",'):
                 line = line.replace('",', '"')
                 comma_needed = False

            # If the line contains one of these characters then it does not need a comma
            if line.strip().endswith('{') or line == "" or line.strip().endswith(',') or line.strip().endswith("["):     
                comma_needed = False

            # Add comma to lines which need it
            if comma_needed:
                line += ','

            # Append the modified line to the list
            modified_lines.append(line)

        # Join the modified lines back into a string
        modified_data = '\n'.join(modified_lines)

        # this is needed to represent the object
        modified_data = "{" + modified_data + "}"

        print("MODIFIED DATA: ", modified_data)

        # Convert string to dictionary
        terraform_dict = eval(modified_data)

        # Print the dictionary
        print("DICTIONARY: ", terraform_dict)

except Exception as e:
    print("An error occurred:", e)
