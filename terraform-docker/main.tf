# This Terraform code provisions Docker on a remote host and then runs a NGINX container on that host

# This block configures Terraform to use the null provider, which is a provider that does nothing. 
# It's typically used for tasks that are not supported by other providers, such as executing local or remote commands.
provider "null" {}

resource "null_resource" "docker_provisioner" {
  # Define connection details to the remote host
  connection {
    type        = "ssh"
    host        = "10.212.174.49"
    user        = "ubuntu"
    private_key = file("/home/ubuntu/.ssh/id_rsa")  # Path to your private key
    timeout     = "2m"
  }

  # Use remote-exec provisioner to install Docker
  provisioner "remote-exec" {
    inline = [
      "curl -fsSL https://get.docker.com -o get-docker.sh",
      "sudo sh get-docker.sh",
      "sudo usermod -aG docker $USER",  # Add current user to the docker group
      "sudo systemctl enable docker",
      "sudo systemctl start docker"
    ]
  }
}
# The above block defines a null resource named docker_provisioner. It uses the remote-exec provisioner to execute a series of shell commands on the remote host via SSH connection. These commands:
# Download the Docker installation script from https://get.docker.com.
# Run the Docker installation script to install Docker.
# Add the current user to the docker group, allowing the user to execute Docker commands without using sudo.
# Enable and start the Docker service.

resource "null_resource" "nginx_container" {
  depends_on = [null_resource.docker_provisioner]
  # The NGINX container (nginx_container) requires Docker to be installed and configured on the remote host 
  # before it can be created. Therefore, we specify the depends_on relationship to ensure that the Docker 
  # provisioning (docker_provisioner) happens before attempting to create the NGINX container.

  # Define connection details to the remote host
  connection {
    type        = "ssh"
    host        = "10.212.174.49"
    user        = "ubuntu"
    private_key = file("/home/ubuntu/.ssh/id_rsa")  # Path to your private key
    timeout     = "2m"
  }

  # Use remote-exec provisioner to run NGINX container
  provisioner "remote-exec" {
    inline = [
      "sudo docker run -d --name nginx_container -p 8000:80 nginx"
    ]
  }
}
# This block defines another null resource named nginx_container, which depends on the docker_provisioner resource. 
# It also uses the remote-exec provisioner to run a Docker command on the remote host. 
# This command starts an NGINX container in detached mode with the name "nginx_container" and maps port 8000 on 
# the host to port 80 inside the container, allowing access to the NGINX web server running inside the container.
