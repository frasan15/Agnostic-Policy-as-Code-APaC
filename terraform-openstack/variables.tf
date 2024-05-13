

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
    default = "port22_exposed"
}

variable "subnet_id" {
    description = "id subnet. N.B. this is just a semplification, I will be fetching this value in the main when I will be implementing the real infrastructure"
    type = string
    default = "cc518030-1241-4d1a-ba60-ffd73772647c"
}

variable "network1" {
    description = "network name of a new network"
    type = string
    default = "network1"
}

variable "subnet1" {
    description = "subnet name"
    type = string
    default = "subnet1"
}


# write all the needed network name, server name, etc. in general all the information needed to retrieve the data you need
# create a variable as an array containing all these parameters
# refer to this data resource with the for each in order to retrieve all the networks, servers, subnets, networks in an ordered way