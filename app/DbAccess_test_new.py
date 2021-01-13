import json
import datetime
from datetime import datetime as dt
from flask_mysqldb import MySQL
import time 
#from app_test_new import *


# def __init__(self, mysql):
#     self.mysql = MySQL(app)
#     self.app = app
#     # print("DBAccess __init__() called")
#     # print(self.mysql)

#mysql = mysql


def query_db(cursor):
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.close()
    return r

def myconverter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')

def retrieve_all_nodes(mysql):

    json_data = {}

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = "select * from nodes"
    result_value = cur.execute(sql)
    if result_value > 0:
        my_query = query_db(cur)
        json_data = json.dumps(my_query, default=myconverter)
    else:
        json_data = {}

    return json_data

def retrieve_all_active_nodes(mysql):
    
    json_data = {}

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = "select * from nodes where heartbeat_status='True'"
    result_value = cur.execute(sql)
    if result_value > 0:
        my_query = query_db(cur)
        json_data = json.dumps(my_query, default=myconverter)

    return json_data


def retrieve_all_virus_total_logs(mysql):
        
        json_data = {}

        # Mysql connection
        cur = mysql.connection.cursor()

        sql = "select * from virus_total_logs"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = query_db(cur)
            json_data = json.dumps(my_query, default=myconverter)

        return json_data


def retrieve_all_general_logs(mysql):
    
    json_data = {}

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = "select * from general_logs"
    result_value = cur.execute(sql)
    if result_value > 0:
        my_query = query_db(cur)
        json_data = json.dumps(my_query, default=myconverter)

    return json_data

def retrieve_all_nids_logs(mysql):
    
    json_data = {}

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = "select * from nids_logs"
    result_value = cur.execute(sql)
    if result_value > 0:
        my_query = query_db(cur)
        json_data = json.dumps(my_query, default=myconverter)

    return json_data

def retrieve_all_nodes_for_heartbeat(mysql):
    json_data = {}

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = "select * from nodes"
    result_value = cur.execute(sql)
    if result_value > 0:
        my_query = query_db(cur)
        json_data = json.loads(json.dumps(my_query, default=myconverter))
    heartbeat_dict = dict()
    for data in json_data:
        # convert the time format to time since epoch
        last_heard = data.get("last_heard")
        last_heard_struct_time_local = time.strptime(last_heard, "%Y-%m-%d %H:%M:%S")
        last_heard_epoch = time.mktime(last_heard_struct_time_local)
        heartbeat_dict[data.get("token")] = {
                'heartbeat_status' : data.get("heartbeat_status"),
                'last_heard' : last_heard_epoch
        }

    return heartbeat_dict

def retrieve_node(token, mysql):
    json_data = {}

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = f"select * from nodes where token='%s'" % (token)
    result_value = cur.execute(sql)
    if result_value > 0:
        my_query = query_db(cur)
        json_data = json.dumps(my_query, default=myconverter)

    return json_data

def create_node(json, mysql):

    #Mysql connection
    cur = mysql.connection.cursor()

    honeynode_name = json['honeynode_name']
    ip_addr = json['ip_addr']
    subnet_mask = json['subnet_mask']
    honeypot_type = json['honeypot_type']
    nids_type = json['nids_type']
    no_of_attacks = json['no_of_attacks']
    date_deployed = json['date_deployed']
    heartbeat_status = json['heartbeat_status']
    last_heard = json['last_heard']
    token = json['token']

    sql = f"insert into nodes(honeynode_name, ip_addr, subnet_mask, honeypot_type, nids_type, no_of_attacks, date_deployed, heartbeat_status, token, last_heard) \
        values('%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s')" % (honeynode_name, ip_addr, subnet_mask, honeypot_type, nids_type, int(no_of_attacks), date_deployed, heartbeat_status, token, last_heard)
    
    result_value = 0

    try:
        result_value = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value

def update_node(json, token, mysql):

    # Mysql connection
    cur = mysql.connection.cursor()

    honeynode_name = '' if not json.__contains__('honeynode_name') else json['honeynode_name']
    ip_addr = '' if not json.__contains__('ip_addr') else json['ip_addr']
    subnet_mask = '' if not json.__contains__('subnet_mask') else json['subnet_mask']
    honeypot_type = '' if not json.__contains__('honeypot_type') else json['honeypot_type']
    nids_type = '' if not json.__contains__('nids_type') else json['nids_type']
    no_of_attacks = '' if not json.__contains__('no_of_attacks') else int(json['no_of_attacks'])
    date_deployed = '' if not json.__contains__('date_deployed') else json['date_deployed']
    heartbeat_status = '' if not json.__contains__('heartbeat_status') else json['heartbeat_status']
    last_heard = '' if not json.__contains__('last_heard') else json['last_heard']

    sql = f"update nodes set honeynode_name=IF('{honeynode_name}' = '', honeynode_name, '{honeynode_name}'), \
        ip_addr=IF('{ip_addr}' = '', ip_addr, '{ip_addr}'), \
        subnet_mask=IF('{subnet_mask}' = '', subnet_mask, '{subnet_mask}'), \
        honeypot_type=IF('{honeypot_type}' = '', honeypot_type, '{honeypot_type}'), \
        nids_type=IF('{nids_type}' = '', nids_type, '{nids_type}'), \
        no_of_attacks=IF('{no_of_attacks}' = '', no_of_attacks, '{no_of_attacks}'), \
        date_deployed=IF('{date_deployed}' = '', date_deployed, '{date_deployed}'), \
        heartbeat_status=IF('{heartbeat_status}' = '', heartbeat_status, '{heartbeat_status}'), \
        last_heard=IF('{last_heard}' = '', last_heard, '{last_heard}') where token='{token}'"

    result_value = 0

    try:
        result_value = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value

def update_node_heartbeat_status(token, json, mysql):

    # Mysql connection
    cur = mysql.connection.cursor()

    heartbeat_status = '' if not json.__contains__('heartbeat_status') else json['heartbeat_status']

    ############### DO EPOCH PARSING HERE ###########################
    last_heard_epoch = '' if not json.__contains__('last_heard') else json['last_heard']
    last_heard_epoch = float(last_heard_epoch)
    last_heard_struct_time = time.localtime(last_heard_epoch)
    last_heard = f"{last_heard_struct_time[0]}-{last_heard_struct_time[1]}-{last_heard_struct_time[2]} {last_heard_struct_time[3]}:{last_heard_struct_time[4]}:{last_heard_struct_time[5]}"
    
    sql = f"update nodes set \
        heartbeat_status=IF('{heartbeat_status}' = '', heartbeat_status, '{heartbeat_status}'), \
        last_heard=IF('{last_heard}' = '', last_heard, '{last_heard}') where token='{token}'"

    result_value = 0

    try:
        result_value = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value

def delete_node(token, mysql):

    # Mysql connection
    cur = mysql.connection.cursor()

    sql = f"delete from nodes where token='{token}'"
    
    result_value = 0

    try:
        result_value = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value



"""
Author: Derek
Database Access for virustotal logs
"""

def insert_vt_log(vt_data, mysql):
    # Mysql connection
    cur = mysql.connection.cursor()

    sql = f"insert into virus_total_logs(resource, scan_id, md5, sha1, sha256, scan_date,permalink,positives, total, scans, zipped_file_path,time_at_file_received, token) \
        values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s')"        
    result_value = 0
    insert_data = (
        vt_data["resource"],
        vt_data["scan_id"],
        vt_data["md5"],
        vt_data["sha1"],
        vt_data["sha256"],
        vt_data["scan_date"],
        vt_data["permalink"],
        vt_data["positives"],
        vt_data["total"],
        json.dumps(vt_data["scans"]),
        vt_data["zipped_file_path"],
        vt_data["time_at_file_received"],
        vt_data["token"],
    )
    try:
        result_value = cur.execute(sql,insert_data)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value


"""
Author: rongtao
Database Access for general logs
"""
def insert_general_log(general_log_data, mysql):
    # Mysql connection
    cur = mysql.connection.cursor()

    sql = f"insert into general_logs(capture_date, honeynode_name, source_ip, source_port, destination_ip, destination_port, protocol, token, raw_logs) \
        values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (general_log_data['capture_date'],
        general_log_data['honeynode_name'],
        general_log_data['source_ip'],
        general_log_data['source_port'],
        general_log_data['destination_ip'],
        general_log_data['destination_port'],
        general_log_data['protocol'],
        general_log_data['token'],
        general_log_data['raw_logs']
    )

    result_value = 0

    try:
        result_value = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value


# Insert NIDS Logs
def insert_snort_log(snort_log_data, mysql):
    cur = mysql.connection.cursor()
    sql = f"insert into general_logs(nids_type,date,honeynode_name,source_ip,source_port,destination_ip, destination_port,priority, classfication,signature, raw_logs) \
        values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('snort',
        snort_log_data['date'],
        snort_log_data['honeynode_name'],
        snort_log_data['source_ip'],
        snort_log_data['source_port'],
        snort_log_data['destination_ip'],
        snort_log_data['destination_port'],
        snort_log_data['priority'],
        snort_log_data['classification'],
        snort_log_data['signature'],
        snort_log_data['raw_logs']
    )

    result_value = 0

    try:
        result_value = cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        print(err)

    return result_value


