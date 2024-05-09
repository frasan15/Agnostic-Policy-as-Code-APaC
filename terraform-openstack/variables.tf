variable "openstack_password" {
    
}

variable "server_name_existing" {
    description = "name of already existing server"
    type = string
    default = "MyThirdServer"
}

variable "server_name" {
    description = "name of the web server"
    type = string
    default = "web_server"
}

variable "network_name" {
    description = "name of the network"
    type = string
    default = "MySecondNetwork"
}

variable "security_groups" {
    description = "security group names"
    type = string
    default = "default"
}

variable "servers_list" {
    description = "list containing each server defined in OpenStack"
    type = list(string)
    default = [var.server_name, var.server_name_existing]
}

# write all the needed network name, server name, etc. in general all the information needed to retrieve the data you need
# create a variable as an array containing all these parameters
# refer to this data resource with the for each in order to retrieve all the networks, servers, subnets, networks in an ordered way