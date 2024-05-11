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

        prov = '''
{
  "network_info": {
    "admin_state_up": True,
    "all_tags": [],
    "availability_zone_hints": [],
    "description": "",
    "dns_domain": "",
    "external": False,
    "id": "b881b3ee-5795-4f8e-b951-19b61a957972",
    "matching_subnet_cidr": null,
    "mtu": 9000,
    "name": "MySecondNetwork",
    "network_id": null,
    "region": "SkyHiGh",
    "segments": [],
    "shared": False,
    "status": null,
    "subnets": [
      "cc518030-1241-4d1a-ba60-ffd73772647c"
    ],
    "tags": null,
    "tenant_id": "630a1bb146cd455f9dcea286cf2347a6",
    "transparent_vlan": False
  },
  "security_group_info": {
    "description": "Expose port 22",
    "id": "50f58a2f-59b7-4e75-81be-354b26ea118b",
    "name": "port22_exposed",
    "rules": [
      {
        "direction": "ingress",
        "ethertype": "IPv4",
        "port_range_max": 22,
        "port_range_min": 22,
        "protocol": "tcp",
        "remote_ip_prefix": "0.0.0.0/0"
      }
    ]
  },
  "server_info": {
    "access_ip_v4": "192.168.110.21",
    "access_ip_v6": "",
    "availability_zone": "nova",
    "created": "2024-05-11 16:44:02 +0000 UTC",
    "flavor_id": "931a16c5-fa1e-4f51-8298-86364b72eb48",
    "flavor_name": "gx1.2c4r",
    "id": "8d048ffb-6cee-42e9-b71e-b399047a4bcf",
    "image_id": "db1bc18e-81e3-477e-9067-eecaa459ec33",
    "image_name": "Ubuntu Server 22.04 LTS (Jammy Jellyfish amd64",
    "key_pair": "MySecondKey",
    "metadata": {},
    "name": "web_server",
    "network": [
      {
        "fixed_ip_v4": "192.168.110.21",
        "fixed_ip_v6": "",
        "mac": "fa:16:3e:9c:e3:fd",
        "name": "MySecondNetwork",
        "port": "",
        "uuid": ""
      }
    ],
    "power_state": "active",
    "region": "SkyHiGh",
    "security_groups": [
      "port22_exposed"
    ],
    "tags": [],
    "updated": "2024-05-11 16:44:26 +0000 UTC",
    "user_data": null
  },
  "server_info_2": {
    "access_ip_v4": "192.168.110.250",
    "access_ip_v6": "",
    "availability_zone": "nova",
    "created": "2024-02-19 11:20:07 +0000 UTC",
    "flavor_id": "8879a5d9-398c-458a-8be9-d2abcb8bd7dc",
    "flavor_name": "sx3.16c32r",
    "id": "9733b23b-26d6-4078-8666-5e65da9e3cea",
    "image_id": "db1bc18e-81e3-477e-9067-eecaa459ec33",
    "image_name": "Ubuntu Server 22.04 LTS (Jammy Jellyfish amd64",
    "key_pair": "MySecondKey",
    "metadata": {},
    "name": "MyThirdServer",
    "network": [
      {
        "fixed_ip_v4": "192.168.110.250",
        "fixed_ip_v6": "",
        "mac": "fa:16:3e:2a:0e:23",
        "name": "MySecondNetwork",
        "port": "",
        "uuid": ""
      }
    ],
    "power_state": "active",
    "region": "SkyHiGh",
    "security_groups": [
      "default"
    ],
    "tags": [],
    "updated": "2024-04-11 09:39:46 +0000 UTC",
    "user_data": null
  },
  "server_instance_ids": [
    "8d048ffb-6cee-42e9-b71e-b399047a4bcf"
  ],
  "subnet_info": {
    "all_tags": [],
    "allocation_pools": [
      {
        "end": "192.168.110.254",
        "start": "192.168.110.2"
      }
    ],
    "cidr": "192.168.110.0/24",
    "description": "",
    "dhcp_disabled": null,
    "dhcp_enabled": null,
    "dns_nameservers": [],
    "enable_dhcp": True,
    "gateway_ip": "192.168.110.1",
    "host_routes": [],
    "id": "cc518030-1241-4d1a-ba60-ffd73772647c",
    "ip_version": 4,
    "ipv6_address_mode": "",
    "ipv6_ra_mode": "",
    "name": "MySecondSubnet-v4",
    "network_id": "b881b3ee-5795-4f8e-b951-19b61a957972",
    "region": "SkyHiGh",
    "service_types": [],
    "subnet_id": "cc518030-1241-4d1a-ba60-ffd73772647c",
    "subnetpool_id": "",
    "tags": null,
    "tenant_id": "630a1bb146cd455f9dcea286cf2347a6"
  }
}
'''

        # Convert string to dictionary
        terraform_dict = eval(modified_data)

        # Print the dictionary
        print("DICTIONARY: ", terraform_dict)

except Exception as e:
    print("An error occurred:", e)
