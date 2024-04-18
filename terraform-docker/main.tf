terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "2.18.0" // Specify the version you want to use
    }
  }
}

# Execute the SSH command to install Docker
resource "null_resource" "install_docker" {
 

  provisioner "local-exec" {
    command = "ssh user@10.212.174.49 'sudo apt-get update && sudo apt-get install -y docker-ce'"
  }
}

# Create a Docker container (you can customize this part as needed)
resource "docker_container" "my_container" {
  name  = "my-docker-container"
  image = "nginx:latest"
  ports {
    internal = 80
    external = 8000
  }
}
