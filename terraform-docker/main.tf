terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "2.18.0" // Specify the version you want to use
    }
  }
}

provider "docker" {
  host = "http://10.212.174.49:2376"
}

# New resource to install Docker on the remote host
resource "null_resource" "install_docker" {
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    command = "ssh user@10.212.174.49 'sudo apt-get update && sudo apt-get install -y docker-ce'"
  }
}

resource "docker_image" "nginx" {
  name = "nginx:latest"
}

resource "docker_container" "nginx" {
  name  = "nginx_container"
  image = docker_image.nginx.latest
  ports {
    internal = 80
    external = 80
  }
}
