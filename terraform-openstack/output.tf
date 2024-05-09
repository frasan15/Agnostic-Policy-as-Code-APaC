output "network_info" {
    value = data.openstack_networking_network_v2.existing_network
}

output "server_info" {
    value = data.openstack_compute_instance_v2.instance
}