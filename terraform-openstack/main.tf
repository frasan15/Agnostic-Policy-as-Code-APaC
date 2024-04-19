# The following Terraform code provisions an OpenStack compute instance (called web server) and associates a 
# floating IP address with it to make it accessible from the Internet

# Define required providers
terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  user_name   = "fransant"
  project_domain_id = "cb782810849b4ce8bce7f078cc193b19"
  user_domain_name = "NTNU"
  tenant_id   = "630a1bb146cd455f9dcea286cf2347a6"
  tenant_name = "TTM4905_V24_fransant"
  password    = var.openstack_password
  auth_url    = "https://api.skyhigh.iik.ntnu.no:5000"
  region      = "SkyHiGh"
}

# Generate a floating ip
resource "openstack_networking_floatingip_v2" "myip"{
  pool = "ntnu-internal"
}

# Create a web server instance
resource "openstack_compute_instance_v2" "web_server" {
  name            = "web_server"
  flavor_name     = "gx1.2c4r"
  image_id        = "db1bc18e-81e3-477e-9067-eecaa459ec33"
  network {
    name = "MySecondNetwork"
  }
  security_groups = ["default"]
  key_pair = "MySecondKey"

    # Provisioners to install and configure Apache web server
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y apache2",
      "echo '<html><head><title>Welcome to My Custom Web Server</title></head><body><h1>Hello, world!</h1><p>This is a custom web server running on port 80.</p></body></html>' | sudo tee /var/www/html/index.html",
      "sudo systemctl restart apache2"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"  # Adjust the username based on your VM's operating system
      private_key = file("/home/ubuntu/.ssh/id_rsa")  # Adjust the path to your private key file
      host        = self.network[0].floating_ip_v4  # Use the fixed IP address of the instance
    }
  }

}

resource "openstack_compute_floatingip_associate_v2" "myip" {
  floating_ip = openstack_networking_floatingip_v2.myip.address
  instance_id = openstack_compute_instance_v2.web_server.id # this is the id of the instance to assoicate the floating ip with
  fixed_ip = openstack_compute_instance_v2.web_server.network.0.fixed_ip_v4 # the fixed ip address of the instance. This ensures that the floating IP is associated with the correct interface on the instance
}