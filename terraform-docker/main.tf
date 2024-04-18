terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {
  # No configuration needed for the provider
}

# Specify the connection to the remote host
resource "null_resource" "remote_provisioner" {
  connection {
    type        = "ssh"
    host        = "10.212.174.49"
    user        = "ubuntu"
    private_key = file("/home/ubuntu/.ssh/id_rsa")  # Path to your SSH private key
  }

  # Install Docker on the remote host
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y docker.io",
    ]
  }
}

# Pull the nginx Docker image
resource "docker_image" "nginx" {
  name         = "nginx"
  keep_locally = false

  # Depend on the null_resource to ensure Docker is installed before attempting to pull the image
  depends_on = [null_resource.remote_provisioner]
}

# Run the nginx container on the remote host
resource "docker_container" "nginx" {
  image         = docker_image.nginx.name
  name          = var.container_name
  network_mode  = "host"  # Bind to the host's network

  # Depend on the Docker image resource
  depends_on = [docker_image.nginx]
}
