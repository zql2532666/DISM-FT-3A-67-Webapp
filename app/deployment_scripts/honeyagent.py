""" 
HeartBeat client: sends an UDP packet to a given server every HELLO_INTERVAL (5 seconds).

Adjust the constant parameters as needed, in honeyagent.conf
"""

from socket import socket, AF_INET, SOCK_DGRAM,SOCK_STREAM
import socket
from time import time, ctime, sleep
import sys
import json
from configparser import ConfigParser
import os 
import socket
import threading
import requests

basedir = os.path.abspath(os.path.dirname(__file__))

"""
heart beat signals will sent to the server (SERVIERIP) per time specified 
by HELLO_INTERVAL
"""
config = ConfigParser()
# honeyagent.conf is generated by the deployment bash script
config.read(os.path.join(basedir, 'honeyagent.conf'))

# WEB SERVER INFO
WEB_SERVER_IP = config['WEB-SERVER']['SERVER_IP']  
WEB_SERVER_PORT = config['WEB-SERVER']['PORT']     
SERVER_HB_PORT = int(config['HEARTBEATS']['SERVER_HB_PORT'])            
HELLO_INTERVAL = int(config['HEARTBEATS']['HELLO_INTERVAL'])               


# HONEYNODE INFO
TOKEN = config['HONEYNODE']['TOKEN']
HONEYNODE_NAME = config['HONEYNODE']['HONEYNODE_NAME']
HONEYNODE_IP = config['HONEYNODE']['IP']
HONEYNODE_SUBNET_MASK = config['HONEYNODE']['SUBNET_MASK']
HONEYNODE_HONEYPOT_TYPE = config['HONEYNODE']['HONEYPOT_TYPE']
HONEYNODE_NIDS_TYPE = config['HONEYNODE']['NIDS_TYPE']
HONEYNODE_DEPLOYED_DATE = config['HONEYNODE']['DEPLOYED_DATE']
HONEYNODE_COMMAND_PORT = int(config['HONEYNODE']['COMMAND_PORT'])

heartbeat_data = {
    "token": TOKEN,
    "msg": "HEARTBEAT"
}

heartbeat_data_json = json.dumps(heartbeat_data)

def send_heartbeats():
    print ("HeartBeat client sending to IP {} , {}".format(WEB_SERVER_IP, SERVER_HB_PORT))
    print ("\n*** Press Ctrl-C to terminate ***\n")
    data_encoded = heartbeat_data_json.encode('utf-8')
    # print(f"heartbeats size: {len(data_encoded)}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hbsocket:
            while 1:
                hbsocket.sendto(data_encoded, (WEB_SERVER_IP, SERVER_HB_PORT))
                print ("Heartbeat Time: {}".format(ctime(time())))
                sleep(HELLO_INTERVAL)
    except socket.error as e:
        print("Error creating HeartBeat Socket\n")
        print(e)

def kill(): 
    print("Shutting Down Virtual Machine")
    cmd = "init 0"
    os.system(cmd)

def add_node():
    payload = {
        "honeynode_name": HONEYNODE_NAME,
        "ip_addr": HONEYNODE_IP,
        "subnet_mask": HONEYNODE_SUBNET_MASK,
        "honeypot_type": HONEYNODE_HONEYPOT_TYPE,
        "nids_type": HONEYNODE_NIDS_TYPE,
        "no_of_attacks": "0",
        "date_deployed": HONEYNODE_DEPLOYED_DATE,
        "heartbeat_status":"False",
        "last_heard": HONEYNODE_DEPLOYED_DATE,
        "token": TOKEN
    }
    payload_json = json.dumps(payload)  
    headers = {'content-type': 'application/json'}
    api_endpoint = "http://{0}:{1}/api/v1/honeynodes/".format(WEB_SERVER_IP,WEB_SERVER_PORT)
    response = requests.post(api_endpoint, data=payload_json, headers=headers)

def listen_for_command():
    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.bind(('', HONEYNODE_COMMAND_PORT))
    while True:
        data, addr = receive_socket.recvfrom(1024)
        data = data.decode('utf-8')
        data = json.loads(data)
        print("data: {} from {}".format(data,addr))
        if data['command'] == 'KILL':
            kill()
        elif data['command'] == 'ADD_NODE':
            add_node()

send_heartbeats_thread = threading.Thread(target=send_heartbeats)
listen_for_command_thread = threading.Thread(target=listen_for_command)
send_heartbeats_thread.start()
listen_for_command_thread.start()
