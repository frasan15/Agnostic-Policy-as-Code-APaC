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
  name = "network1"
  admin_state_up = "true"
}

# Create a subnet within the previously created network
resource "openstack_networking_subnet_v2" "subnet_1" {
  name = "subnet1"
  network_id = openstack_networking_network_v2.network_1.id
  cidr = "192.168.111.0/24"
  ip_version = 4
}

# Define a security group which exposes port 80
resource "openstack_networking_secgroup_v2" "secgroup_1" {
  name        = "secgroup_1"
  description = "Expose port 80" # remember to change this if you modify the rules
}

# Specifically, you define the rules hereby
# If you want to define other rules, then you have the define other resources like the one below
# N.B. the parameter security_group_id below refers to the previous created security group
resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_1" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.secgroup_1.id
}

resource "openstack_networking_secgroup_v2" "secgroup_2" {
  name = "secgroup_2"
  description = "Expose port 22"
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_2" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.secgroup_2.id
}

resource "openstack_networking_secgroup_v2" "secgroup_3" {
  name = "secgroup_3"
  description = "Expose port 443"
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_3" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.secgroup_2.id
}

# Define a port (or interface) to connect the server to the newly created subnet; defining a port means 
# to specify the subnet id where to connect the server to, and the ip address this interface will have
# this ip address is basically the ip address of the server itself
resource "openstack_networking_port_v2" "port_server_1" {
  name = "port_server_1"
  network_id = openstack_networking_network_v2.network_1.id
  admin_state_up = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_1.id]

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet_1.id
    ip_address = "192.168.111.10"
  }
}

resource "openstack_networking_port_v2" "port_server_2" {
  name = "port_server_2"
  network_id = openstack_networking_network_v2.network_1.id
  admin_state_up = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_2.id]

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet_1.id
    ip_address = "192.168.111.11"
  }
}

resource "openstack_networking_port_v2" "port_server_3" {
  name = "port_server_3"
  network_id = openstack_networking_network_v2.network_1.id
  admin_state_up = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_3.id]

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet_1.id
    ip_address = "192.168.111.12"
  }
}

# Create the first server instance which exposes port 80
resource "openstack_compute_instance_v2" "server_1" {
  depends_on = [ openstack_networking_secgroup_rule_v2.secgroup_rule_1 ]
  name            = "server1"
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    port = openstack_networking_port_v2.port_server_1.id
  }
  security_groups = [openstack_networking_secgroup_v2.secgroup_1.name]
  key_pair = "MySecondKey"

}

# Create the second server instance which exposes port 22
resource "openstack_compute_instance_v2" "server_2" {
  depends_on = [ openstack_networking_secgroup_rule_v2.secgroup_rule_2 ]
  name            = "server2"
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    port = openstack_networking_port_v2.port_server_2.id
  }
  security_groups = [openstack_networking_secgroup_v2.secgroup_2.name]
  key_pair = "MySecondKey"

}

# Create the third server instance which exposes port 443
resource "openstack_compute_instance_v2" "server_3" {
  depends_on = [ openstack_networking_secgroup_rule_v2.secgroup_rule_3 ]
  name            = "server3"
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    port = openstack_networking_port_v2.port_server_3.id
  }
  security_groups = [openstack_networking_secgroup_v2.secgroup_3.name]
  key_pair = "MySecondKey"

}

# Define a router -> among the other things, this is needed to generate a floating ip from the right pool, since the router will be connected to ntnu-internal network
resource "openstack_networking_router_v2" "router_1" {
  name = "router1"
  admin_state_up = "true"
  external_network_id = "730cb16e-a460-4a87-8c73-50a2cb2293f9" # ntnu-internal
}

# Define a router interface to connect the newly created router with the previously created network
resource "openstack_networking_router_interface_v2" "router_interface_1" {
  router_id = openstack_networking_router_v2.router_1.id
  subnet_id = openstack_networking_subnet_v2.subnet_1.id
}

# Generate a floating ip for server1
resource "openstack_networking_floatingip_v2" "myip"{
  depends_on = [ openstack_compute_instance_v2.server_1, openstack_networking_router_interface_v2.router_interface_1 ]
  pool = "ntnu-internal"
  port_id = openstack_networking_port_v2.port_server_1.id
}

# Generate a floating ip for server3
resource "openstack_networking_floatingip_v2" "myip"{
  depends_on = [ openstack_compute_instance_v2.server_3, openstack_networking_router_interface_v2.router_interface_1 ]
  pool = "ntnu-internal"
  port_id = openstack_networking_port_v2.port_server_3.id
}


# ERROR: The following module is shown in the documentation but it's not found once terraform apply is executed

#data "openstack_networking_floatingip_v2" "floatingip_1" {
#  depends_on = [ openstack_networking_floatingip_v2.myip ]
#  address = "192.168.111.10"
#}
