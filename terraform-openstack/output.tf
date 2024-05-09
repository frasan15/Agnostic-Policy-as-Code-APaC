# Output the server instance IDs
output "server_instance_ids" {
  value = locals.server_instance_ids
}

#output "server_info" {
#    value = data.openstack_compute_instance_v2.instance
#}