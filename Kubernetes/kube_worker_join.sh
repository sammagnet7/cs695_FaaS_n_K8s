#!/bin/bash
#Install dependencies
# - Docker Engine
# - Add user to docker group
# - cri-dockerd
#   - GO
# - kubeadm, kubectl, kubelet
# run the following after node restarts
sudo swapoff -a
sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
chmod +x join.sh
sudo ./join.sh
rm join.sh
