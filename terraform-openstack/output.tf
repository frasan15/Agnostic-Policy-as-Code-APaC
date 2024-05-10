# Print the ids's list -> there's still the \n problem to fix
output "server_instance_ids" {
  value = local.server_instance_ids
}

# Output the server instance IDs
output "server_info" {
    value = data.openstack_compute_instance_v2.server_info
}