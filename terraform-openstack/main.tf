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
  user_name   = "frasant"
  tenant_name = "TTM4905_V24_fransant"
  password    = var.openstack_password
  auth_url    = "https://api.skyhigh.iik.ntnu.no:5000"
  region      = "SkyHiGh"
}

# Define an instance flavor
resource "openstack_compute_flavor_v2" "web_server_flavor" {
  name     = "gx1.2c4r"
  ram      = 4096  # RAM in MB
  vcpus    = 2     # Number of virtual CPUs
  disk     = 40    # Disk size in GB
}

# Define an image for the web server
resource "openstack_compute_image_v2" "web_server_image" {
  name = "Ubuntu Server 22.04 LTS (Jammy Jellyfish) amd64"
  # Specify the image ID or customize as needed
  image_id = "db1bc18e-81e3-477e-9067-eecaa459ec33"
}

# Define a network for the web server
data "openstack_networking_network_v2" "web_server_network" {
  name = "MySecondNetwork"
  # Specify network details or customize as needed
}

# Define a security group for the web server
data "openstack_networking_secgroup_v2" "web_server_secgroup" {
  name        = "default"
  description = "defaut security group"
  # Define security group rules as needed
}

# Create a web server instance
resource "openstack_compute_instance_v2" "web_server" {
  name            = "web_server"
  flavor_name     = openstack_compute_flavor_v2.web_server_flavor.name
  image_id        = openstack_compute_image_v2.web_server_image.id
  network {
    uuid = openstack_networking_network_v2.web_server_network.id
  }
  security_groups = [openstack_networking_secgroup_v2.web_server_secgroup.name]
  # Customize additional instance configuration as needed

  # Example: Use cloud-init to configure the web server
  user_data = <<-EOF
              #!/bin/bash
              # Your cloud-init script to configure the web server
              echo "Hello, World! This is a custom web server." > /var/www/html/index.html
              # Add more configuration as needed
              EOF
}
