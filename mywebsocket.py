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

info = "/api/system/info"
bitaxe_ip = "192.168.1.233"
logs_folder = "./logs"
http_window_seconds = 5

start_time = time.strftime("%Y-%m-%d_%H-%M-%S")

ws_output_file = f"{logs_folder}/ws_{start_time}.log"
info_output_file = f"{logs_folder}/info_{start_time}.log"

def on_message(ws, message):
    msg = "### new ws message ###"
    print(msg)
    print(message)
    write_log(msg,ws_output_file)
    write_log(message,ws_output_file)
    
def on_error(ws, error):
    msg = "### ws ERROR ###"
    print(f"{msg} error={error}")
    write_log(f"{msg} error={error}",ws_output_file)

def on_close(ws, close_status_code, close_msg):
    msg = "### ws closed ###"
    print(msg)
    write_log(msg,ws_output_file)
    print ("Retry : %s" % time.ctime())
    write_log("Retry : %s" % time.ctime(),ws_output_file)
    time.sleep(20)
    connect_ws() # retry per 20 seconds

def on_open(ws):
    msg = "### Opened ws connection ###"
    print(msg)
    write_log(msg,ws_output_file)

def get_info():
    msg = "### HTTP Info ###"
    while True:
        try:
            contents = urllib.request.urlopen("http://" + bitaxe_ip + info).read()
        except:
            print("Ups! something went wrong! Disconnected?")
            os._exit(1)
        
        j = json.loads(contents)
        print(msg)
        for key in j.keys():
            text = f" {key}: {j[key]}"
            print(text)
            if(key=="uptimeSeconds"):
                print(f" UPTIME (, hh:mm:ss): {str(datetime.timedelta(seconds=j[key]))}")
            write_log(text, info_output_file)

        time.sleep(http_window_seconds)
    
def connect_ws():
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://" + bitaxe_ip + "/api/ws" ,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(reconnect=10)

def write_log(output, file_name):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    fp = open(file_name, "a")
    fp.write(f"{current_time}: {output}")
    fp.write("\n")
    fp.close()
    
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

    thread_info = threading.Thread(target=get_info, args=())
    thread_info.start()
    
    if args['nowebsocket']:
        print("Connection WebSokciet disabled!")
    else:
        connect_ws()
        print("WS END!")
        sys.exit(1)

