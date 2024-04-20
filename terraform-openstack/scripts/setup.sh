#!/bin/bash
# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

set -x

# Install necessary dependencies
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade
sudo apt-get update
sudo apt-get -y -qq install curl wget git vim apt-transport-https ca-certificates
sudo add-apt-repository ppa:longsleep/golang-backports -y
sudo apt-get -y -qq install golang-go

# Setup sudo to allow no-password sudo for "hashicorp" group and adding "terraform" user
sudo groupadd -r hashicorp
sudo useradd -m -s /bin/bash terraform
sudo usermod -a -G hashicorp terraform
sudo cp /etc/sudoers /etc/sudoers.orig
echo "terraform  ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/terraform

# Installing SSH key
sudo mkdir -p /home/ubuntu/.ssh
sudo chmod 700 /home/ubuntu/.ssh
sudo echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCM3bB7L7kesUSb0aXchVHtSoV29cWWDUO9z8C7vQkMD4atBuO407NAQ0Wbhn30twyz3UjwKckttvvPneNOlktCdj03IcVr7Endc1vxBpInCDkjWTcEJVLlGOjlLWrN5jto+fUckegyL5k80/ulYIlRlNnajId44LhKFpW6wjUlSLmFgglFAncBXzOit8piijAgCNCQLb7zukCmY55kuqeOV7yd2+OJ52UjkPbFdPh/kYgsPKY/flCSCODJqBB+3LIL/bZCEboHaZNRGi64EN+DIPiPg/qVG3l2oFqiBKQkaBC318KDdnblSY0BbEe9q2pdI/ck2tLal55rvyD9Ey2h8Fcy+TGgy9+7KTyu/ntym8mY+uNfK/OykU/eGTbn0E9WCHcpz73+jpCIeHwZMkDwi+KPL0gSkQBNSUoyMSf6kaURQ/LZgRgwMuKBj6twyCa9/8McVWvDvrZCq1so227erk3M5OPR2Xdsedvbkp8jtVQjLAbT9v1H7gJk90TG5vhy4YjpohyRU6d9DkchAQzVkXtFeeMXX5d6pFHit3F3cN/PefP8k2/y1CqxaN+mBHsBnm8ErrONiXM7W4ZcfK40Cum2LZ7wUS3MOyrUHD5cwwY++AKFjGeB+a99+I+4qP7/x49M5aKZq/WoIEt1kAi/Ls457UqlvixSQpeI+iX8kQ== ubuntu@mythirdserver" >> /home/ubuntu/.ssh/authorized_keys
sudo chmod 600 /home/ubuntu/.ssh/authorized_keys
sudo chown -R terraform /home/ubuntu/.ssh
sudo usermod --shell /bin/bash terraform

# Create GOPATH for Terraform user & download the webapp from github

sudo -H -i -u terraform -- env bash << EOF
whoami
echo ~terraform

cd /home/terraform

export GOROOT=/usr/lib/go
export GOPATH=/home/terraform/go
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
git clone https://github.com/hashicorp/learn-go-webapp-demo.git
EOF