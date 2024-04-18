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

resource "null_resource" "nginx_container" {
  depends_on = [null_resource.docker_provisioner]

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
