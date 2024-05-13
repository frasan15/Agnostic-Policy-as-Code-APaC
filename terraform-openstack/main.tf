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

# Create a network
resource "openstack_networking_network_v2" "network_1" {
  name = var.network1
  admin_state_up = "true"
}

# Create a subnet within the previously created network
resource "openstack_networking_subnet_v2" "subnet_1" {
  name = var.subnet1
  network_id = openstack_networking_network_v2.network_1.id
  cidr = "192.168.111.0/24"
  ip_version = 4
}

# Define a security group which exposes port 22
resource "openstack_networking_secgroup_v2" "secgroup_1" {
  name        = var.security_groups
  description = "Expose port 22"
}

# Specifically, you define the rules hereby
# If you want to define other rules, then you have the define other resources like the one below
# N.B. the parameter security_group_id below refers to the previous created security group
resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_1" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.secgroup_1.id
}

# Define a port (or interface) to connect the server to the newly created subnet; defining a port means 
# to specify the subnet id where to connect the server to, and the ip address this interface will have
# this ip address is basically the ip address of the server itself
resource "openstack_networking_port_v2" "port_1" {
  name = "port_1"
  network_id = openstack_networking_network_v2.network_1.id
  admin_state_up = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_1.id]

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet_1.id
    ip_address = "192.168.111.10"
  }
}

# Create a web server instance
resource "openstack_compute_instance_v2" "web_server" {
  depends_on = [ openstack_networking_secgroup_rule_v2.secgroup_rule_1 ]
  name            = var.server_name
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    port = openstack_networking_port_v2.port_1.id
  }
  security_groups = [openstack_networking_secgroup_v2.secgroup_1.name]
  key_pair = "MySecondKey"

# The following provisioner writes into the file server_ids.txt the id of the newly created server (N.B. I will use this file as a list of all the server's ids created)
# TODO: fix the \n problem
  provisioner "local-exec" {
    command = "echo '\n' >> server_ids.txt; echo '${self.id}' >> server_ids.txt"
  }

}

# Define a router -> among the other things, this is needed to generate a floating ip from the right pool, since the router will be connected to ntnu-internal network
resource "openstack_networking_router_v2" "router_1" {
  name = var.router1
  admin_state_up = "true"
  external_network_id = "730cb16e-a460-4a87-8c73-50a2cb2293f9"
}

# Define a router interface to connect the newly created router with the previously created network
resource "openstack_networking_router_interface_v2" "router_interface_1" {
  router_id = openstack_networking_router_v2.router_1.id
  subnet_id = openstack_networking_subnet_v2.subnet_1.id
}

# Generate a floating ip
resource "openstack_networking_floatingip_v2" "myip"{
  depends_on = [ openstack_compute_instance_v2.web_server, openstack_networking_router_interface_v2.router_interface_1 ]
  pool = "ntnu-internal"
  port_id = openstack_networking_port_v2.port_1.id
}

# Define all the information needed for the subnet here below
# This is needed since Terraform-OpenStack registry does not provide any function to retrieve such info
# about subnets

# TODO: look at the dependencies below, try to associate floating ip to fixed ip with another resource (the one above is deprecated)
#       find a nice way of exporting the information whether a server has a floating ip or not; since you can use this to determine whether is connected to Internet or not -> ASK TO PALMA MAYBE

locals {
  depends_on = [ openstack_networking_secgroup_rule_v2.secgroup_rule_1, openstack_networking_floatingip_v2.myip ]
  secgroup_info = {
    name        = openstack_networking_secgroup_v2.secgroup_1.name
    description = openstack_networking_secgroup_v2.secgroup_1.description
    id = openstack_networking_secgroup_v2.secgroup_1.id
    rules = [
      {
        direction       = openstack_networking_secgroup_rule_v2.secgroup_rule_1.direction
        ethertype       = openstack_networking_secgroup_rule_v2.secgroup_rule_1.ethertype
        protocol        = openstack_networking_secgroup_rule_v2.secgroup_rule_1.protocol
        port_range_min  = openstack_networking_secgroup_rule_v2.secgroup_rule_1.port_range_min
        port_range_max  = openstack_networking_secgroup_rule_v2.secgroup_rule_1.port_range_max
        remote_ip_prefix = openstack_networking_secgroup_rule_v2.secgroup_rule_1.remote_ip_prefix
      }
    ]
  }
  #float_ip = {
  #  de = openstack_compute_instance_v2.web_server
    #fixed_ip = openstack_networking_floatingip_v2.myip.fixed_ip
    #floating_ip = openstack_networking_floatingip_v2.myip.address
    #entire = openstack_networking_floatingip_v2.myip
  #}
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

# I fetch information about web server newly created
# N.B. If you need to fetch information from other server as well, you need to use the same code asking for the
# corresponding server's id
data "openstack_compute_instance_v2" "server_info" {
  id = openstack_compute_instance_v2.web_server.id
}

data "openstack_compute_instance_v2" "server_info_2" {
  id = "9733b23b-26d6-4078-8666-5e65da9e3cea"
}

data "openstack_networking_network_v2" "network" {
  name = var.network1
}

data "openstack_networking_secgroup_v2" "secgroup" {
  depends_on = [ openstack_networking_secgroup_rule_v2.secgroup_rule_1 ]
  name = var.security_groups
}

data "openstack_networking_subnet_v2" "subnet_1" {
  subnet_id = var.subnet1
}

data "openstack_networking_router_v2" "router" {
  name = var.router1
}

data "openstack_networking_floatingip_v2" "floatingip_1" {
  address = "192.168.111.10"
}
