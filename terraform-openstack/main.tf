# The following Terraform code provisions an OpenStack compute instance (called web server) and associates a 
# floating IP address with it to make it accessible from the Internet

# Define required providers
terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  user_name   = "fransant"
  project_domain_id = "cb782810849b4ce8bce7f078cc193b19"
  user_domain_name = "NTNU"
  tenant_id   = "630a1bb146cd455f9dcea286cf2347a6"
  tenant_name = "TTM4905_V24_fransant"
  password    = var.openstack_password
  auth_url    = "https://api.skyhigh.iik.ntnu.no:5000"
  region      = "SkyHiGh"
}

# Generate a floating ip
resource "openstack_networking_floatingip_v2" "myip"{
  pool = "ntnu-internal"
}

# Create a web server instance
resource "openstack_compute_instance_v2" "web_server" {
  name            = var.server_name
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    name = var.network_name
  }
  security_groups = [var.security_groups]
  key_pair = "MySecondKey"

# The following provisioner writes into the file server_ids.txt the id of the newly created server (N.B. I will use this file as a list of all the server's ids created)
# TODO: fix the \n problem
  provisioner "local-exec" {
    command = "echo '\n' >> server_ids.txt; echo '${self.id}' >> server_ids.txt"
  }

}

# Read server instance IDs from the file
data "local_file" "server_ids_file" {
  depends_on = [openstack_compute_instance_v2.web_server]
  filename   = "server_ids.txt"
}

# Store the ids' list inside server_instance_ids, splitting them by \n character
# Filter out values == ""
locals {
  server_instance_ids = [for id in split("\n", data.local_file.server_ids_file.content) : id if id != ""]
}

# After catching all the ids, the file server_ids.txt is resetted
resource "null_resource" "delete_file" {
  depends_on = [ local.server_instance_ids ]
  provisioner "local-exec" {
    command = "echo '' > server_ids.txt"
  }
}

locals {
  depends_on = [local.server_instance_ids]
  // Define static keys for server_info_map
  static_server_instance_keys = [
    "server1",
    "server2"
  ]
  
  // Map the static keys to values present in local.server_instance_ids
  server_info_map = {
    for idx, key in local.static_server_instance_keys :
    key => idx < length(local.server_instance_ids) ? local.server_instance_ids[idx] : null
    if idx < length(local.server_instance_ids) // Only include if the condition is satisfied
  }
}


data "openstack_compute_instance_v2" "server_info" {
  depends_on = [ local.server_info_map ]
  for_each = {
    for key, value in local.server_info_map :
    key => value != "" ? value : null // Include only non-empty values
  }

  id = each.value
}



