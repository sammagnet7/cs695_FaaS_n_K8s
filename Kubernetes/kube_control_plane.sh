#!/bin/bash
#Install dependencies
# - Docker Engine
# - Add user to docker group
# - cri-dockerd
#   - GO
# - kubeadm, kubectl, kubelet
# run the following after node restarts
# Turn off swap
sudo swapoff -a
# Reset configurations
sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
# Restart control plane
sudo kubeadm init --control-plane-endpoint=10.157.3.213 --pod-network-cidr=192.168.0.0/16 --cri-socket=unix:///var/run/cri-dockerd.sock
# Store the worker join command
sudo kubeadm token create --print-join-command > join.sh
sed -i '$s|$| --cri-socket=unix:///var/run/cri-dockerd.sock|' join.sh
scp join.sh arif@10.157.3.45:~/
# Setup kubectl config
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
# Run the CNI
curl https://raw.githubusercontent.com/projectcalico/calico/v3.27.3/manifests/calico.yaml -O
sleep 5
kubectl apply -f calico.yaml
# untainting control plane
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
# Run the loadbalancer on control plane
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.4/config/manifests/metallb-native.yaml
# Configure IP pool
kubectl create -f metallb_config.yaml
# Retaint control plane
kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule
# Deploy ingress controller
helm upgrade --install ingress-nginx ingress-nginx   --repo https://kubernetes.github.io/ingress-nginx   --namespace ingress-nginx --create-namespace
kubectl delete ValidatingWebhookConfiguration ingress-nginx-admission
# Control plane ready
