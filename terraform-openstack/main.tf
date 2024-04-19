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

# Define a key pair for the web server
resource "openstack_compute_keypair_v2" "test-keypair" {
  name = "MySecondKey"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYDh6gZ6qOjaPcRy492ply6PngBhUeRMNM4PSl1CQgwlOLNncoXd5PyBTHIggJxqcn+pizbjoxdrulvsFD5v/GcLGLEXQptzud4kYhic2L/8tCwrLPJdOlhgMqpTiBzVc2khSeRert/7Nt1XhzSJA0pRWZYBVUrddtetWKAilbmnRKv68aXrZuhAX1oXS/0LRIR63dypeUQ80WapQ3wvKurYTYvVQDUNkUxim+RcrGcd6k/nIMeDDcJafPqulVmh60ekHC0TGgh85WLCK0yxFMY2t4rMDlHRvd1k3SQTjmaZB4xlO6iFB+XryWZ2QG8fbVQrsCTlZB0yaNJg2ZQAVD"
}

# Create a web server instance
resource "openstack_compute_instance_v2" "web_server" {
  name            = "web_server"
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    uuid = data.openstack_networking_network_v2.web_server_network.id
  }
  security_groups = [data.openstack_networking_secgroup_v2.web_server_secgroup.name]
  key_pair = openstack_compute_keypair_v2.test-keypair
}