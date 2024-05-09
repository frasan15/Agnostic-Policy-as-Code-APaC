output "networks" {
  value = data.openstack_networking_network_v2.existing_networks[*].name
}

output "server_info" {
    value = data.openstack_compute_instance_v2.instance
}