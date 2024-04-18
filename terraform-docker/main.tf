provider "null" {}

resource "null_resource" "docker_installation" {
  # Define connection details to the remote host
  connection {
    type        = "ssh"
    host        = "10.212.174.49"
    user        = "ubuntu"
    private_key = file("/home/ubuntu/.ssh/id_rsa")  # Path to your private key
    timeout     = "2m"
  }

  # Check if Docker is installed, if not, download and install Docker
  provisioner "remote-exec" {
    inline = [
      "if ! command -v docker &> /dev/null; then",
      "  curl -fsSL https://get.docker.com -o get-docker.sh",
      "  sudo sh get-docker.sh",
      "  sudo usermod -aG docker $USER",  # Add current user to the docker group
      "  sudo systemctl enable docker",
      "  sudo systemctl start docker",
      "fi"
    ]
  }
}

resource "null_resource" "nginx_container" {
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
      "sudo docker run -d --name nginx_container -p 80:80 nginx"
    ]
  }
}
