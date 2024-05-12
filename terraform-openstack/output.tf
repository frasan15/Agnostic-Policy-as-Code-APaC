# Print the ids's list -> there's still the \n problem to fix
output "server_instance_ids" {
  value = local.server_instance_ids
}

# Output the server instance IDs
output "server_info" {
    value = data.openstack_compute_instance_v2.server_info
}

# Output the server instance IDs
output "server_info_2" {
    value = data.openstack_compute_instance_v2.server_info_2
}

output "servers" {
  value = [data.openstack_compute_instance_v2.server_info,
  data.openstack_compute_instance_v2.server_info_2
  ]
}

output "network_info" {
  value = data.openstack_networking_network_v2.network
}

output "security_group_info" {
  value = local.secgroup_info
}

output "subnet_info" {
  value = data.openstack_networking_subnet_v2.subnet_1
}