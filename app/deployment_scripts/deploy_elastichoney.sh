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


systemctl disable apt-daily-upgrade.service || true

apt update

sudo rm /var/lib/dpkg/lock* || true
sudo dpkg --configure -a || true

apt-get -y install git golang supervisor curl python-pip python3-pip
pip install configparser
pip install requests

# install honeyagent
mkdir /opt/honeyagent
cd /opt/honeyagent
wget http://$SERVER_IP:$SERVER_PORT/api/v1/deploy/deployment_script/honeyagent -O honeyagent.py
wget http://$SERVER_IP:$SERVER_PORT/api/v1/deploy/deployment_script/honeyagent_conf_file -O honeyagent.conf

# populate the honeyagent config file
sed -i "s/TOKEN:/TOKEN: $TOKEN/g" honeyagent.conf
sed -i "s/HONEYNODE_NAME:/HONEYNODE_NAME: $HONEYNODE_NAME/g" honeyagent.conf
sed -i "0,/IP:/s/IP:/IP: $IP_ADDR/g" honeyagent.conf
sed -i "s/SUBNET_MASK:/SUBNET_MASK: $SUBNET/g" honeyagent.conf
sed -i "s/HONEYPOT_TYPE:/HONEYPOT_TYPE: elastichoney/g" honeyagent.conf
sed -i "s/NIDS_TYPE:/NIDS_TYPE: snort/g" honeyagent.conf
sed -i "s/DEPLOYED_DATE:/DEPLOYED_DATE: $DEPLOY_DATE/g" honeyagent.conf
sed -i "s/SERVER_IP:/SERVER_IP: $SERVER_IP/g" honeyagent.conf

# Get the elastichoney source
cd /opt
git clone https://github.com/zql2532666/elastichoney.git
cd elastichoney

export GOPATH=/opt/elastichoney
go get || true
go build

# api call to join the honeynet
curl -X POST -H "Content-Type: application/json" -d "{
	\"honeynode_name\" : \"$HONEYNODE_NAME\",
	\"ip_addr\" : \"$IP_ADDR\",
	\"subnet_mask\" : \"$SUBNET\",
	\"honeypot_type\" : \"elastichoney\",
	\"nids_type\" : \"snort\",
	\"no_of_attacks\" : \"0\",
	\"date_deployed\" : \"$DEPLOY_DATE\",
	\"heartbeat_status\" : \"False\",
	\"last_heard\" : \"$DEPLOY_DATE\",
	\"token\" : \"$TOKEN\"
}" http://$SERVER_IP:$SERVER_PORT/api/v1/honeynodes/ || true


# hpfeeds config
HPF_HOST=$SERVER_IP  
HPF_PORT=$(cat /opt/honeyagent/honeyagent.conf | grep "HPFEEDS_PORT" | awk -F: '{print $2}' | xargs)
HPF_IDENT=$TOKEN
HPF_SECRET=$TOKEN

cat > config.json<<EOF
{
    "logfile" : "/opt/elastichoney/elastichoney.log",
    "use_remote" : false,
    "hpfeeds": {
        "enabled": true,
        "host": "$HPF_HOST",
        "port": $HPF_PORT,
        "ident": "$HPF_IDENT",
        "secret": "$HPF_SECRET",
        "channel": "elastichoney.events"
    },
    "instance_name" : "Green Goblin",
    "anonymous" : true,
    "spoofed_version"  : "1.4.1"
}
EOF

# Config for supervisor.
cat > /etc/supervisor/conf.d/elastichoney.conf <<EOF
[program:elastichoney]
command=/opt/elastichoney/elastichoney
directory=/opt/elastichoney
stdout_logfile=/opt/elastichoney/elastichoney.out
stderr_logfile=/opt/elastichoney/elastichoney.err
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

# supervisorctl update