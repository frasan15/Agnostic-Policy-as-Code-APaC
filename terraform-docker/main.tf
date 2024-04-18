terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "2.18.0" // Specify the version you want to use
    }
  }
}

provider "docker" {
  host = "tcp://10.212.174.49:2375"
}

resource "docker_image" "nginx" {
  name         = "nginx:latest"
}

resource "docker_container" "nginx" {
  name  = "nginx_container"
  image = docker_image.nginx.latest
  ports {
    internal = 80
    external = 80
  }
}
