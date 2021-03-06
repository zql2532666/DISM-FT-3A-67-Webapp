#!/bin/bash

set -e
set -x

if [ $# -ne 4 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_ip> <server_port> <honeynode_token> <honeynode_name>"
        exit 1
fi

SERVER_IP=$1
SERVER_PORT=$2
TOKEN=$3
HONEYNODE_NAME=$4

INTERFACE=$(basename -a /sys/class/net/e*)
IP_ADDR=$(ip addr show dev $INTERFACE | grep "inet" | awk 'NR==1{print $2}' | cut -d '/' -f 1)
SUBNET=$(ifconfig $INTERFACE | grep "Mask:" | awk '{print $4}' | cut -d ':' -f 2)
DEPLOY_DATE=$(date +"%Y-%m-%d %T")


# Install dependencies
systemctl disable apt-daily-upgrade.service || true

apt update

sudo rm /var/lib/dpkg/lock* || true
sudo dpkg --configure -a || true

apt --yes install \
    git \
    supervisor \
    build-essential \
    cmake \
    check \
    cython3 \
    libcurl4-openssl-dev \
    libemu-dev \
    libev-dev \
    libglib2.0-dev \
    libloudmouth1-dev \
    libnetfilter-queue-dev \
    libnl-3-dev \
    libpcap-dev \
    libssl-dev \
    libtool \
    libudns-dev \
    python3 \
    python3-dev \
    python3-bson \
    python3-yaml \
    python3-boto3 \
    python-pip \
    python3-pip \
    curl

pip install configparser
pip3 install watchdog
pip3 install pathlib

# fetching honeyagent script + config file from the server
mkdir /opt/honeyagent
cd /opt/honeyagent
wget http://$SERVER_IP:$SERVER_PORT/api/v1/deploy/deployment_script/honeyagent -O honeyagent.py
wget http://$SERVER_IP:$SERVER_PORT/api/v1/deploy/deployment_script/honeyagent_conf_file -O honeyagent.conf

# populate the honeyagent config file
sed -i "s/TOKEN:/TOKEN: $TOKEN/g" honeyagent.conf
sed -i "s/HONEYNODE_NAME:/HONEYNODE_NAME: $HONEYNODE_NAME/g" honeyagent.conf
sed -i "0,/IP:/s/IP:/IP: $IP_ADDR/g" honeyagent.conf
sed -i "s/SUBNET_MASK:/SUBNET_MASK: $SUBNET/g" honeyagent.conf
sed -i "s/HONEYPOT_TYPE:/HONEYPOT_TYPE: dionaea/g" honeyagent.conf
sed -i "s/NIDS_TYPE:/NIDS_TYPE: snort/g" honeyagent.conf
sed -i "s/DEPLOYED_DATE:/DEPLOYED_DATE: $DEPLOY_DATE/g" honeyagent.conf
sed -i "s/SERVER_IP:/SERVER_IP: $SERVER_IP/g" honeyagent.conf

# fetch the watchdog script from the server
mkdir /opt/dionaea_binary_uploader
cd /opt/dionaea_binary_uploader
wget http://$SERVER_IP:$SERVER_PORT/api/v1/deploy/deployment_script/watchdog -O dionaea_binary_uploader.py
    
cd ~
git clone https://github.com/zql2532666/dionaea.git
cd dionaea

# Latest tested version with this install script
git checkout baf25d6

# api call to join the honeynet
curl -X POST -H "Content-Type: application/json" -d "{
	\"honeynode_name\" : \"$HONEYNODE_NAME\",
	\"ip_addr\" : \"$IP_ADDR\",
	\"subnet_mask\" : \"$SUBNET\",
	\"honeypot_type\" : \"dionaea\",
	\"nids_type\" : \"snort\",
	\"no_of_attacks\" : \"0\",
	\"date_deployed\" : \"$DEPLOY_DATE\",
	\"heartbeat_status\" : \"False\",
	\"last_heard\" : \"$DEPLOY_DATE\",
	\"token\" : \"$TOKEN\"
}" http://$SERVER_IP:$SERVER_PORT/api/v1/honeynodes/ || true


mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX:PATH=/opt/dionaea ..

make
make install

# hpfeeds config
HPF_HOST=$SERVER_IP  
HPF_PORT=$(cat /opt/honeyagent/honeyagent.conf | grep "HPFEEDS_PORT" | awk -F: '{print $2}' | xargs)
HPF_IDENT=$TOKEN
HPF_SECRET=$TOKEN

cat > /opt/dionaea/etc/dionaea/ihandlers-enabled/hpfeeds.yaml <<EOF
- name: hpfeeds
  config:
    # fqdn/ip and port of the hpfeeds broker
    server: "$HPF_HOST"
    port: $HPF_PORT
    ident: "$HPF_IDENT"
    secret: "$HPF_SECRET"
    # dynip_resolve: enable to lookup the sensor ip through a webservice
    # dynip_resolve: "http://canhazip.com/"
    # Try to reconnect after N seconds if disconnected from hpfeeds broker
    # reconnect_timeout: 10.0
EOF

sed -i "s/listen.mode=getifaddrs/listen.mode=manual/g" /opt/dionaea/etc/dionaea/dionaea.cfg
sed -i "s/# listen.addresses=127.0.0.1/listen.addresses=$IP_ADDR/g" /opt/dionaea/etc/dionaea/dionaea.cfg

# Editing configuration for Dionaea.
mkdir -p /opt/dionaea/var/log/dionaea/wwwroot /opt/dionaea/var/log/dionaea/binaries /opt/dionaea/var/log/dionaea/log
chown -R nobody:nogroup /opt/dionaea/var/log/dionaea

mkdir -p /opt/dionaea/var/log/dionaea/bistreams 
chown nobody:nogroup /opt/dionaea/var/log/dionaea/bistreams

# Config for supervisor.
cat > /etc/supervisor/conf.d/dionaea.conf <<EOF
[program:dionaea]
command=/opt/dionaea/bin/dionaea -c /opt/dionaea/etc/dionaea/dionaea.cfg
directory=/opt/dionaea/
stdout_logfile=/opt/dionaea/var/log/dionaea.out
stderr_logfile=/opt/dionaea/var/log/dionaea.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

# configure supervisor for honeyagent
cat > /etc/supervisor/conf.d/honeyagent.conf <<EOF
[program:honeyagent]
command=python3 /opt/honeyagent/honeyagent.py
directory=/opt/honeyagent
stdout_logfile=/opt/honeyagent/honeyagent.out
stderr_logfile=/opt/honeyagent/honeyagent.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

# configure supervisor for watchdog
cat > /etc/supervisor/conf.d/dionaea_binary_uploader.conf <<EOF
[program:dionaea_binary_uploader]
command=python3 /opt/dionaea_binary_uploader/dionaea_binary_uploader.py
directory=/opt/dionaea_binary_uploader
stdout_logfile=/opt/dionaea_binary_uploader/dionaea_binary_uploader.out
stderr_logfile=/opt/dionaea_binary_uploader/dionaea_binary_uploader.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF