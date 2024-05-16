terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

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

  #network_mode = "none"  # Disable default networking
  networks_advanced {
    name = docker_network.network1.name
    ipv4_address = "192.168.111.10"
  }

  ports {
    internal = 80
    external = 80
  }
}

resource "docker_container" "server2" {
  image = docker_image.nginx.image_id
  name  = "server2"

  #network_mode = "none"  # Disable default networking
  networks_advanced {
    name = docker_network.network1.name
    ipv4_address = "192.168.111.11"
  }

  ports {
    internal = 22
    external = 22
  }
}
