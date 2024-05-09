output "networks" {
  value = [for network in data.openstack_networking_network_v2.existing_networks : {
    name = network.name
    id   = network.id
    # Add more attributes as needed
  }]
}

output "server_info" {
    value = data.openstack_compute_instance_v2.instance
}