provider "docker" {
  host = "tcp://10.212.174.49:2376"
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
