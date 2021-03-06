import json
import datetime
from datetime import datetime as dt
from flask_mysqldb import MySQL
import time 

class DbAccess:

    def __init__(self, app):
        self.mysql = MySQL(app)

    def query_db(self, cursor):
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        return r

    def myconverter(self,obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

    def retrieve_all_nodes(self):
    
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select * from nodes"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)
        else:
            json_data = {}

        return json_data

    def retrieve_all_active_nodes(self):
        
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select * from nodes where heartbeat_status='True'"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)

        return json_data

    def retrieve_all_general_logs(self):
        
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select * from general_logs"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)

        return json_data

    def retrieve_all_virus_total_logs(self):
        
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select *, (select honeynode_name from nodes where virus_total_logs.token = nodes.token) as honeynode_name from virus_total_logs;"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)

        return json_data

    def retrieve_all_nids_logs(self):
        
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select * from nids_logs"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)

        return json_data

    def retrieve_all_session_logs(self):
        
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select * from session_logs"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)

        return json_data

    def retrieve_all_nodes_for_heartbeat(self):
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "select * from nodes"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.loads(json.dumps(my_query, default=self.myconverter))
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

    def retrieve_node(self, token):
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = f"select * from nodes where token='%s'" % (token)
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)

        return json_data

    def create_node(self, json):

        #Mysql connection
        cur = self.mysql.connection.cursor()

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
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    def update_node(self, json, token):

        # Mysql connection
        cur = self.mysql.connection.cursor()

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
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    def update_node_heartbeat_status(self, token, json):
    
        # Mysql connection
        cur = self.mysql.connection.cursor()

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
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    def delete_node(self, token):

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = f"delete from nodes where token='{token}'"
        
        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value



    """
    Author: Derek
    Database Access for virustotal logs
    """

    def insert_vt_log(self, vt_data):
        # Mysql connection
        cur = self.mysql.connection.cursor()
        scan_id  = vt_data["scan_id"]
        md5 = vt_data["md5"]
        sha1 =  vt_data["sha1"]
        sha256 =  vt_data["sha256"]
        scan_date =  vt_data["scan_date"]
        permalink = vt_data["permalink"]
        positives =  int(vt_data["positives"])
        total =  int(vt_data["total"])
        scans =  json.dumps(vt_data["scans"])
        zipped_file_path =  vt_data["zipped_file_path"]
        time_at_file_received =  vt_data["time_at_file_received"]
        token =  vt_data["token"]
        response = int(vt_data["response_code"])
        zipped_file_password = vt_data["zipped_file_password"]

        # sql = f"insert into virus_total_logs(scan_id, md5, sha1, sha256, scan_date, permalink,positives, total, scans, zipped_file_path,time_at_file_received, token) \
        #     values(%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s')" % (scan_id,md5,sha1,sha256,scan_date,permalink,positives,total,scans,zipped_file_path,time_at_file_received,token)
        sql = f"insert into virus_total_logs(scan_id, md5, sha1, sha256, scan_date, permalink,positives, total, scans, zipped_file_path,time_at_file_received, token,response, zipped_file_password) \
            values(\
                '{scan_id}',\
                '{md5}', \
                '{sha1}', \
                '{sha256}',\
                '{scan_date}', \
                '{permalink}', \
                '{positives}', \
                '{total}', \
                '{scans}', \
                '{zipped_file_path}', \
                '{time_at_file_received}',\
                '{token}',\
                '{response}',\
                '{zipped_file_password}')"     
        result_value = 0
        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    def insert_vt_log_file_path(self, vt_data):
        cur = self.mysql.connection.cursor()
        md5 = vt_data["md5"]
        zipped_file_path =  vt_data["zipped_file_path"]
        time_at_file_received =  vt_data["time_at_file_received"]
        token =  vt_data["token"]
        response = int(vt_data["response_code"])
        zipped_file_password = vt_data["zipped_file_password"]       
        print("\n\n----VT DATA ---- \n\n")
        print(vt_data)
        print("\n\n----VT DATA ---- \n\n")
        sql = f"insert into virus_total_logs(md5, zipped_file_path,time_at_file_received, token,response,zipped_file_password) \
            values(\
                '{md5}', \
                '{zipped_file_path}', \
                '{time_at_file_received}',\
                '{token}',\
                '{response}',\
                '{zipped_file_password}')"     
        result_value = 0
        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value


    """
    Author: rongtao
    Database Access for general logs
    """
    def insert_general_log(self, general_log_data):
        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = f"insert into general_logs(capture_date, honeynode_name, source_ip, source_port, destination_ip, destination_port, protocol, token, raw_logs) \
            values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            general_log_data['capture_date'],
            general_log_data['honeynode_name'],
            general_log_data['source_ip'],
            general_log_data['source_port'],
            general_log_data['destination_ip'],
            general_log_data['destination_port'],
            general_log_data['protocol'],
            general_log_data['token'],
            general_log_data['raw_logs']
        )
        print('\n\n')
        print("type in insert")
        print(type(general_log_data['raw_logs']))
        result_value = 0

        try:
            result_value = cur.execute(sql)
            print("\n\n")
            print("insert raw log")
            print(general_log_data['raw_logs'])
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value


    # Insert NIDS Logs
    def insert_snort_log(self,snort_log_data):
        cur = self.mysql.connection.cursor()
        nids_type = 'snort'
        sql = f"insert into nids_logs(nids_type,date,token,honeynode_name,source_ip,source_port,destination_ip, destination_port,priority, classification,signature, raw_logs) \
            values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            nids_type,
            snort_log_data['date'],
            snort_log_data['token'], 
            snort_log_data['honeynode_name'],
            snort_log_data['source_ip'],
            snort_log_data['source_port'],
            snort_log_data['destination_ip'],
            snort_log_data['destination_port'],
            snort_log_data['priority'],
            snort_log_data['classification'],
            snort_log_data['signature'],
            snort_log_data['raw_logs'])

        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    
    # Insert cowrie session logs
    def insert_session_log(self, session_log_data):
        cur = self.mysql.connection.cursor()

        token = session_log_data['token']
        honeynode_name = session_log_data['honeynode_name']
        source_ip = session_log_data['source_ip']
        source_port = session_log_data['source_port']
        destination_ip = session_log_data['destination_ip']
        destination_port = session_log_data['destination_port']
        commands = json.dumps(session_log_data['commands'])
        logged_in = json.dumps(session_log_data['logged_in'])
        start_time = session_log_data['start_time']
        end_time = session_log_data['end_time']
        session = session_log_data['session']
        urls = json.dumps(session_log_data['urls'])
        credentials = json.dumps(session_log_data['credentials'])
        hashes = json.dumps(session_log_data['hashes'])
        version = session_log_data['version']
        unknown_commands = json.dumps(session_log_data['unknown_commands'])


        sql = f"insert into session_logs(token,honeynode_name,source_ip,source_port,destination_ip, destination_port, commands, logged_in, start_time, end_time, session, urls, credentials, hashes, version, unknown_commands) \
            values( \
            '{token}', \
            '{honeynode_name}', \
            '{source_ip}', \
            '{source_port}', \
            '{destination_ip}', \
            '{destination_port}', \
            '{commands}', \
            '{logged_in}', \
            '{start_time}', \
            '{end_time}', \
            '{session}', \
            '{urls}', \
            '{credentials}', \
            '{hashes}', \
            '{version}', \
            '{unknown_commands}')"

        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value


    def update_bruteforce_log(self, bruteforce_log_data):
        cur = self.mysql.connection.cursor()
        
        token = bruteforce_log_data['token']
        start_time = bruteforce_log_data['start_time']
        end_time = bruteforce_log_data['end_time']
        source_ip = bruteforce_log_data['source_ip']
        credentials = json.dumps(bruteforce_log_data['credentials'])

        sql = f"update session_logs set end_time='{end_time}', credentials='{credentials}' where token = '{token}' and source_ip = '{source_ip}' and start_time='{start_time}'"

        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            
            sql1 = f"SELECT log_id, raw_logs from general_logs where token = '{token}' and source_ip = '{source_ip}'"
            result_value_1 = cur.execute(sql1)
            if result_value_1 > 0:
                rows = self.query_db(cur)
                for row in rows:
                    raw_log_dict = json.loads(row['raw_logs'])
                    if raw_log_dict['startTime'].split(".")[0].replace("T", " ") == start_time:
                        raw_log_dict_new = raw_log_dict
                        raw_log_dict_new['credentials'] = bruteforce_log_data['credentials']

                        sql3 = f"update general_logs set raw_logs='%s' where log_id = %d" % (json.dumps(raw_log_dict_new), row['log_id'])
                        print("\n\n")
                        print("sql query")
                        print(sql3)

                        result_value_2 = cur.execute(sql3)
                        self.mysql.connection.commit()
                        print(result_value_2)
                        
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    
    def delete_general_logs_by_id(self, log_id_list):
        cur = self.mysql.connection.cursor()
        # log_id_list = [69, 70, 71, 72]

        place_holders = ', '.join(["'%s'"] * len(log_id_list))
        sql = f"delete from general_logs where log_id in ({place_holders})" % tuple(log_id_list)

        print(sql)
        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return 0

        return result_value


    def delete_snort_logs_by_id(self, log_id_list):
        cur = self.mysql.connection.cursor()

        place_holders = ', '.join(["'%s'"] * len(log_id_list))
        sql = f"delete from nids_logs where nids_log_id in ({place_holders})" % tuple(log_id_list)
        print(sql)
        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return 0

        return result_value

    
    def delete_session_logs_by_id(self, log_id_list):
        cur = self.mysql.connection.cursor()

        place_holders = ', '.join(["'%s'"] * len(log_id_list))
        sql = f"delete from session_logs where session_log_id in ({place_holders})" % tuple(log_id_list)
        print(sql)

        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return 0

        return result_value

    
    def delete_vt_logs_by_id(self, log_id_list):
        cur = self.mysql.connection.cursor()

        place_holders = ', '.join(["'%s'"] * len(log_id_list))
        sql = f"delete from virus_total_logs where id in ({place_holders})" % tuple(log_id_list)
        print(sql)

        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)
            return 0

        return result_value

    """
    Data correlation sql methods
    """
    def retrieve_all_general_logs_last_24_hours(self):
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "SELECT * FROM general_logs where capture_date >= now() - INTERVAL 1 DAY;"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)
        return json_data

    def retrieve_all_nids_logs_last_24_hours(self):
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = "SELECT * FROM nids_logs where `date` >= now() - INTERVAL 1 DAY;"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)
        return json_data

    def retrieve_all_general_logs_date_range(self, start_date, end_date):
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = f"SELECT * FROM general_logs where capture_date between '{start_date}' and '{end_date}';"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)
        return json_data

    def retrieve_all_nids_logs_date_range(self, start_date, end_date):
        json_data = {}

        # Mysql connection
        cur = self.mysql.connection.cursor()

        sql = f"SELECT * FROM nids_logs where `date` between '{start_date}' and '{end_date}';"
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)
        return json_data

    def check_user_exists(self, email):
    
        json_data = {}

        cur = self.mysql.connection.cursor()

        sql = f"select * from user where name='{email}'"
        cur.execute(sql)
        
        result_value = cur.execute(sql)
        if result_value > 0:
            my_query = self.query_db(cur)
            json_data = json.dumps(my_query, default=self.myconverter)
        else:
            json_data = "{}"

        return json_data

    def update_password(self, password, email):
        
        cur = self.mysql.connection.cursor()

        sql = f"update user set \
            password='{password}' where email='{email}'"

        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value

    def insert_user(self, email, name, password):
    
        cur = self.mysql.connection.cursor()

        sql = f"insert into user(email, name, password) \
            values('%s', '%s', '%s')" % (email, name, password)


        result_value = 0

        try:
            result_value = cur.execute(sql)
            self.mysql.connection.commit()
            cur.close()
        except Exception as err:
            print(err)

        return result_value