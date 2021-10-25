#!/usr/bin/env bash

# run as root

apt-get update

# get docker
apt-get install docker.io

# add user
USER_NAME=$(who | awk {'print $1'})
usermod -aG docker ${USER_NAME}
