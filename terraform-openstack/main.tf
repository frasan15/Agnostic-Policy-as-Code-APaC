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
data "openstack_networking_floatingip_v2" "myip"{
  pool = "ntnu-internal"
}

# Create a web server instance
resource "openstack_compute_instance_v2" "web_server" {
  name            = "web_server"
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    name = "MySecondNetwork"
  }
  security_groups = ["default"]
  key_pair = "MySecondKey"
}

resource "openstack_compute_floatingip_associate_v2" "myip" {
  floating_ip = data.openstack_networking_floatingip_v2.myip.address
  instance_id = openstack_compute_instance_v2.web_server.id
  fixed_ip = openstack_compute_instance_v2.web_server.network.0.fixed_ip_v4
}