terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

resource "docker_image" "nginx" {
  name         = "nginx"
  keep_locally = false
}

# Define a Docker network
resource "docker_network" "network1" {
  name   = "network1"
  driver = "bridge"
  ipam_config {
    subnet = "192.168.111.0/24"
  }
}

resource "docker_container" "server1" {
  image = docker_image.nginx.image_id
  name  = "server1"

  networks_advanced {
    name = docker_network.network1.name
    ipv4_address = "192.168.111.10"
  }
/*
  networks_advanced {
    name = docker_network.network2.name
    ipv4_address = "192.168.112.10"
  }

   ports {
    internal = 80
    external = 8000
    ip = "192.168.111.0/24" # default value for this is 0.0.0.0/0
    protocol = "tcp"
   }
*/
    ports {
      internal = 80
      external = 8000
      ip = "0.0.0.0/0" # default value for this is 0.0.0.0/0
      protocol = "tcp"
    }
}

resource "docker_container" "server2" {
  image = docker_image.nginx.image_id
  name  = "server2"

  networks_advanced {
    name = docker_network.network1.name
    ipv4_address = "192.168.111.11"
  }

  ports {
    internal = 22
    external = 8001
    ip = "255.255.255.255/0" # can I say "if this ip == 0.0.0.0/0 then it is reachable from outside? Or maybe if ip !== 192.168.111.0/24"
    protocol = "tcp"
   }
}

resource "docker_container" "server3" {
  image = docker_image.nginx.image_id
  name  = "server3"

  networks_advanced {
    name = docker_network.network1.name
    ipv4_address = "192.168.111.12"
  }

  ports {
    internal = 443
    external = 8002
    ip = "0.0.0.0/0" # can I say "if this ip == 0.0.0.0/0 AND internal == 80 then it is reachable from outside? Or maybe if ip !== 192.168.111.0/24"
    protocol = "tcp"
   }
}