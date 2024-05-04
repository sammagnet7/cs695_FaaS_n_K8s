# cs695_FaaS_n_K8s
This creates a FAAS platform on top of Kubernetes

# Kubernetes setup

## Installation
Install the following tools in all nodes that will be part of cluster
### Docker Engine
1. Uninstall previous installations 
    ```bash
    $ for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

    ```
2. Setup apt repository
   ```bash
   # Add Docker's official GPG key:
    $ sudo apt-get update
    $ sudo apt-get install ca-certificates curl
    $ sudo install -m 0755 -d /etc/apt/keyrings
    $ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    $ sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    $ echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    $ sudo apt-get update
   ```
3. Install docker packages
    ```bash
    $ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```
4. Verify installation
    ```bash
    $ sudo docker run hello-world
    ```
### Post Installation Steps
The Docker daemon always runs as the root user. If you don't want to preface the docker command with sudo, create a Unix group called docker and add users to it.

1. Create docker group
   ```bash
   $ sudo groupadd docker
   ```
2. Add your user to the docker group
   ```bash
   $ sudo usermod -aG docker $USER
   ```
3. Activate changes to the group
   ```bash
   $ newgrp docker
   ```
4. Verify 
   ```bash
   $ docker run hello-world
   ```
### Container Runtime
1. Install prerequisites
   ```bash
   $ sudo apt-get install git-all
   ```
2. Download Go
   ```bash
   $ wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
   ```
3. Setup Go 
   ```bash
   $ sudo  rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz
   $ sudo export PATH=$PATH:/usr/local/go/bin
   $ source ~/.profile
   ```
4. Download cri-dockerd
   ```bash
   $ git clone https://github.com/Mirantis/cri-dockerd.git
   ```
5. Install cri-dockerd
   ```bash
   $ cd cri-dockerd/
   $ sudo ARCH=amd64 make cri-dockerd
   $ sudo install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd
   $ sudo install packaging/systemd/* /etc/systemd/system
   $ sudo sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service
   ```
6. Enable cri-dockerd daemon
   ```bash
   $ sudo systemctl daemon-reload
   $ sudo systemctl enable --now cri-docker.socket
   ```

### Install tools for cluster setup
1. Install prerequisites
   ```bash
   $ sudo apt-get install -y apt-transport-https ca-certificates curl gpg
   ```
2. Add GPG key
   ```bash
   $ sudo mkdir -p -m 755 /etc/apt/keyrings
   $ sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
   $ echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
   ```
3. Install cluster tools
   ```bash
   $ sudo apt-get update
   $ sudo apt-get install -y kubelet kubeadm kubectl
   $ sudo apt-mark hold kubelet kubeadm kubectl
   ```
4. Enable kubelet service
   ```bash
    $ sudo systemctl enable --now kubelet
   ```

## Cluster Setup
The cluster will have one control plane node and multiple worker nodes.


Execute following steps in the node you want as control plane
### Control plane
1. Turn off swap
   ```bash
   $ sudo swapoff -a
   ```
2. Reset config
   ```bash
   $ sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
   ```
3. Start control plane
   ```bash
   $ sudo kubeadm init --control-plane-endpoint=10.157.3.213 --pod-network-cidr=192.168.0.0/16 --cri-socket=unix:///var/run/cri-dockerd.sock
   ```
4. Setup config
   ```bash
   $ rm -rf $HOME/.kube || true
   $ mkdir -p $HOME/.kube
   $ sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
   $ sudo chown $(id -u):$(id -g) $HOME/.kube/config
   ```
5. Setup CNI(calico)
   ```bash
   $ curl https://raw.githubusercontent.com/projectcalico/calico/v3.27.3/manifests/calico.yaml -O
   $ kubectl apply -f calico.yaml
   ```
6. Deploy filebeat for log collection(optional)
   ```bash
   $ kubectl apply -f filebeat-aio.yaml
   ```
7. Generate worker join command
   ```bash
   $ sudo kubeadm token create --print-join-command
   ```
   The command in the above output is required to join worker nodes in cluster. lets call it ```JOIN_COMMAND```

For every node that you want as worker run the following
### Worker
1. Turnoff swap
   ```bash
   $ sudo swapoff -a
   ```
2. Reset config
   ```bash
   $ sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
   ```
3. Join cluster
   ```bash
   $ JOIN_COMMAND --cri-socket=unix:///var/run/cri-dockerd.sock
   ```


## ELK setup:

Blog:
https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-22-04#step-1-installing-and-configuring-elasticsearch

### 1. Elastic search:

```bash
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch |sudo gpg --dearmor -o /usr/share/keyrings/elastic.gpg```

echo "deb [signed-by=/usr/share/keyrings/elastic.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list

sudo apt update

sudo apt install elasticsearch

sudo nano /etc/elasticsearch/elasticsearch.yml
```
```
	transport.host: localhost 
	transport.tcp.port: 9300 
	http.port: 9200
	network.host: 0.0.0.0
```
```bash
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
curl -X GET "localhost:9200"

sudo cat /etc/elasticsearch/jvm.options.d/custom.options
```

Modify JVM Heap Size:
```bash
nano /etc/elasticsearch/jvm.options
```
```
	-Xms1g
	-Xmx1g
```

### 3. Kibana:

```bash
sudo apt install kibana
sudo systemctl enable kibana
sudo nano /etc/kibana/kibana.yml
```
	server.port: 5601
	server.host: 0.0.0.0
	elasticsearch.hosts: ["http://localhost:9200"]

```bash
sudo systemctl status kibana
sudo netstat -tulpn | grep ':80'
curl -L "http://10.157.3.213:5601/status"
```

### 3. Logstash

```bash
wget --quiet --output-document=- https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor | sudo tee /usr/share/keyrings/elasticsearch-archive-keyring.gpg
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update
sudo apt install --assume-yes logstash
sudo nano /etc/logstash/logstash.yml	

sudo nano /etc/logstash/conf.d/logstash.conf
```
```
input {
  beats {
    port => 5044
  }
}
filter {
        prune {
                whitelist_names => [ "^message$", "^@timestamp$","^kubernetes$" , "^log$" ]
                blacklist_names => [ "_ignored" ]
         }
        mutate {
                remove_field => [ "[kubernetes][container]","[kubernetes][pod][uid]", "[kubernetes][pod][ip]", "[kubernetes][node]", "[kubernetes][labels]", "[kubernetes][namespace_labels]", "[kubernetes][daemonset]", "[kubernetes][namespace_uid]", "[log][file]" ]
        }
    }

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "logindex_%{[kubernetes][namespace]}_%{+YYYY.MM.dd}"
  }
}
```
```bash
sudo systemctl enable logstash
sudo systemctl start logstash
sudo systemctl status logstash

sudo systemctl restart logstash

tail -300 /var/log/logstash/logstash-plain.log  [ OR  ]   sudo journalctl -u logstash | tail -100


sudo /usr/share/logstash/bin/logstash --path.settings /etc/logstash/ --path.data sensor39 -f /etc/logstash/conf.d/logstash.conf

sudo nano /etc/systemd/system/logstash.service
```
```
[Unit]
Description=logstash

[Service]
Type=simple
User=root
Group=root
# Load env vars from /etc/default/ and /etc/sysconfig/ if they exist.
# Prefixing the path with '-' makes it try to load, but if the file doesn't
# exist, it continues onward.
EnvironmentFile=-/etc/default/logstash
EnvironmentFile=-/etc/sysconfig/logstash
ExecStart=/usr/share/logstash/bin/logstash --path.settings /etc/logstash/ -f /etc/logstash/conf.d/logstash.conf
Restart=always
WorkingDirectory=/
Nice=19
LimitNOFILE=16384
```

When stopping, how long to wait before giving up and sending SIGKILL?
Keep in mind that SIGKILL on a process can cause data loss.
TimeoutStopSec=infinity

```
[Install]
WantedBy=multi-user.target

systemctl daemon-reload
```

Kibana url for sorting with multiple fields and to order log entries:
```
http://10.157.3.213:5601/app/discover#/?_a=(columns:(message),filters:!(),index:'5e8dc630-fd98-11ee-b01c-e13c3a690dc4',interval:s,query:(language:kuery,query:'kubernetes.namespace:runner'),sort:!(!('@timestamp',desc),!('log.offset',desc)))&_g=(filters:!(),query:(language:kuery,query:''),refreshInterval:(pause:!f,value:5000),time:(from:now-60m,to:now))
```

Kibana Devtool query logs:
```
GET _cat/indices?v&s=index:asc&health=yellow&h=index,status,docs.count,store.size
GET logindex_*/_search
DELETE logindex_*
```

## Redis setup:
```bash
sudo apt install redis
sudo systemctl status redis

sudo nano /etc/redis/redis.conf
```
```
#bind 127.0.0.1 ::1
protected-mode no
```

```bash
sudo systemctl restart redis-server

redis-cli
keys *
SET key1 "Hello"
MGET key1
LPUSH mylist "world"
LRANGE jobs 0 -1

telnet 10.157.3.213 6379
close
```

To start and stop redis:
```
/etc/init.d/redis-server restart  
/etc/init.d/redis-server stop 
/etc/init.d/redis-server start 
```
On Mac 
```bash
redis-cli shutdown
```
