# Print the ids's list -> there's still the \n problem to fix
# output "server_instance_ids" {
#  value = local.server_instance_ids
#}

output "servers" {
  value = [
    data.openstack_compute_instance_v2.server_info,
    data.openstack_compute_instance_v2.server_info_2
  ]
}

output "networks" {
  value = [
    data.openstack_networking_network_v2.network
  ]
}

output "security_groups" {
  value = [
    local.secgroup_info
  ]
}

output "floatingip" {
  value = local.float_ip
  sensitive = true
}

output "subnets" {
  value = [
    data.openstack_networking_subnet_v2.subnet_1
  ]
}

output "router" {
  value = data.openstack_networking_router_v2.router
}
