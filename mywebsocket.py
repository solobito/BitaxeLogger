# https://github.com/websocket-client/websocket-client
#
# python3 -m venv .venv
# source .venv/bin/activate
# python3 -m pip install -r requirements.txt

import websocket
import time
import urllib.request
import json
import threading
import os
import argparse
import sys
import datetime
import sqlite3
from urllib.error import HTTPError, URLError
from socket import timeout

info = "/api/system/info"
bitaxe_ip = "192.168.1.233"
logs_folder = "./db"
db_name = "./db/bitaxe_database.db"
http_window_seconds = 5

start_time = time.strftime("%Y-%m-%d_%H-%M-%S")

ws_output_file = f"{logs_folder}/ws_{start_time}.log"
info_output_file = f"{logs_folder}/info_{start_time}.log"

def on_message(ws, message):
    msg = "### new ws message ###"
    print(msg)
    print(message)
    write_ws_log(msg,ws_output_file)
    write_ws_log(message,ws_output_file)
    
def on_error(ws, error):
    msg = "### ws ERROR ###"
    print(f"{msg} error={error}")
    write_ws_log(f"{msg} error={error}",ws_output_file)

def on_close(ws, close_status_code, close_msg):
    msg = "### ws closed ###"
    print(msg)
    write_ws_log(msg,ws_output_file)
    print ("Retry : %s" % time.ctime())
    write_ws_log("Retry : %s" % time.ctime(),ws_output_file)
    time.sleep(20)
    connect_ws() # retry per 20 seconds

def on_open(ws):
    msg = "### Opened ws connection ###"
    print(msg)
    write_ws_log(msg,ws_output_file)

def get_info():
    msg = "### HTTP Info ###"
    url = "http://" + bitaxe_ip + info
    name = 'get_info'
    while True:
        try:
            contents = urllib.request.urlopen(url, timeout=5).read()
        except HTTPError as error:
            print(f'HTTP Error: Data of {name} not retrieved because {error}\nURL: {url}')
        except URLError as error:
            if isinstance(error.reason, timeout):
                print(f'Timeout Error: Data of {name} not retrieved because {error}\nURL: {url}')
            else:
                print(f'URL Error: Data of {name} not retrieved because {error}\nURL: {url}')
        else:
            print('\n### NEW INFO MSG ###')
            j = json.loads(contents)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f" {current_time}")
            info_str = f"INSERT INTO stats VALUES ('{current_time}', "
            
            for key in j.keys():
                info_str += f"'{j[key]}', "
                print(f"  {key}: {j[key]}")
                if(key=="uptimeSeconds"):
                    info_str += f"'{str(datetime.timedelta(seconds=j[key]))}', "
                    print(f"  UPTIME: {str(datetime.timedelta(seconds=j[key]))}")
                    
            info_str = info_str[:-2] + ");"
            query_sqlite(info_str,db_name)
            
        time.sleep(http_window_seconds)
    
def connect_ws():
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://" + bitaxe_ip + "/api/ws" ,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(reconnect=10)

def write_ws_log(output, file_name):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    fp = open(file_name, "a")
    fp.write(f"{current_time}: {output}")
    fp.write("\n")
    fp.close()
    
def create_sqlite_table(table_name,db_name):

    connection_obj = sqlite3.connect(db_name)
    cursor_obj = connection_obj.cursor()
 
    # Drop the GEEK table if already exists.
    # cursor_obj.execute("DROP TABLE IF EXISTS GEEK")
 
    table = " CREATE TABLE if not exists " + table_name + \
                 " ("                       \
                 "datetime TEXT, "           \
                 "power DOUBLE, "           \
                 "voltage DOUBLE, "         \
                 "current DOUBLE, "         \
                 "fanSpeedRpm INT, "        \
                 "temp INT, "               \
                 "hashRate DOUBLE, "        \
                 "bestDiff TEXT, "          \
                 "bestSessionDiff TEXT, "   \
                 "freeHeap INT, "           \
                 "coreVoltage INT, "        \
                 "coreVoltageActual INT, "  \
                 "frequency DOUBLE, "       \
                 "ssid TEXT, "              \
                 "hostname TEXT, "          \
                 "wifiStatus TEXT, "        \
                 "sharesAccepted INT, "     \
                 "sharesRejected INT, "     \
                 "uptimeSeconds INT, "      \
                 "uptimeHuman TEXT, "       \
                 "ASICModel TEXT, "         \
                 "stratumURL TEXT, "        \
                 "stratumPort INT, "        \
                 "stratumUser TEXT, "       \
                 "version TEXT, "           \
                 "boardVersion TEXT, "      \
                 "runningPartition TEXT, "  \
                 "flipscreen INT, "         \
                 "invertscreen INT, "       \
                 "invertfanpolarity INT, "  \
                 "autofanspeed INT, "       \
                 "fanspeed INT "            \
                "); "
                
    cursor_obj.execute(table)
    connection_obj.close()
    
def query_sqlite(query,db_name):

    conn = sqlite3.connect(db_name) 
    cursor = conn.cursor() 
  
    cursor.execute(query) 
    conn.commit() 
    conn.close()
    
def check_log_folder():

    if not os.path.exists(logs_folder):
        print(f"Folder {logs_folder} does not exits. Then I create it...") 
        os.makedirs(logs_folder)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Save the Bitaxe WebSocket and http logs in a file')
    parser.add_argument('-ip','--ip', help='The local IP address of your Bitaxe: (E.g. 192.168.1.233)', required=True)
    parser.add_argument('-nowebsocket','--nowebsocket', help='Disable the websocket connection. (On by default)', required=False, action='store_true')
    args = vars(parser.parse_args())

    if 'ip' in args: 
        bitaxe_ip = args['ip']
    else:
        sys.exit(0)
        
    check_log_folder()
    create_sqlite_table("stats","./db/bitaxe_database.db")

    thread_info = threading.Thread(target=get_info, args=())
    thread_info.start()
    
    if args['nowebsocket']:
        print("Connection WebSokciet disabled!")
    else:
        connect_ws()
        print("WS END!")
        sys.exit(1)
        

