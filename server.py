#!/usr/bin/env python3 

import socket
import re
import threading
import time
import select   
import subprocess
from _thread import *

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

start = time.time()
end = 20
####  -----------IP & PORT -------------####

PORT = 12345    
Local_IP = get_ip()
search_NET = re.search(r'\b(?:[0-9]{1,3}\.){2}[0-9]{1,3}\b' , Local_IP)
Local_NET = search_NET.group()
buffer_size = 1024 
####  --------------------------------  #### 

old_packet = ""
start_time = 0
name = input("Enter your name : ")
RSSI = 0

Online_Users = []


def send_packet(HOST , packet):

    global PORT
    
    packet = packet.encode('ascii' , 'replace')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((HOST , PORT))
            s.sendall(packet)

    except:
        print("User is not online any more or invalid IP address")
        for user in Online_Users:
            if user[1] == HOST :
                Online_Users.remove(user)

def listen_TCP_packets():

    global PORT
    global Local_IP

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((Local_IP , PORT))
        s.listen()

        while True:
            conn , addr = s.accept()
            data = conn.recv(buffer_size)
            if not data :
                break

            string = str(data.decode('ascii' , 'replace'))
            receive(string)
            conn.close()

def listen_broadcast():

    global PORT
    global buffer_size
    global Local_IP
    global old_packet
    global start_time
    

    with socket.socket(socket.AF_INET , socket.SOCK_DGRAM) as s:

        s.bind(('', PORT ))
        s.setblocking(0)

        while True:

            result = select.select([s], [], [])

            if not result:
                break

            message = result[0][0].recv(buffer_size)

            if not message:
                break

            
            string = str(message.decode('ascii' , 'replace'))
            end_time = time.time()
            elapsed_time = end_time - start_time
            elapsed_time = float(format(elapsed_time , 'f'))
            string = string[1:][:-1]
            username = string.split(",")[0].strip()
            IP = string.split(",")[1].strip()
            packet_type = string.split(",")[2].strip() 

            if Local_IP != IP and (old_packet != string or elapsed_time > 5) :
            #if (old_packet != string or elapsed_time > 5) :
                if [username , IP] not in Online_Users:
                    Online_Users.append([username , IP])

                print("\n")
                print("#####################")
                print("Quick Notification : ")
                print(username + " opened chat client")
                print("#####################")
                print("\n")
                print("Please continue to write your instruction or command below")


                packet = "[" + name + ", " + Local_IP + ", " + "response" + "]"

                #packet_type = announce , response back with unicast TCP
                start_new_thread(send_packet,(IP , packet))

            old_packet = string
            start_time = end_time

def receive(string):
    global RSSI
    global start, end

    string = string[1:][:-1]
    username = string.split(",")[0].strip()
    IP = string.split(",")[1].strip()
    packet_type = ""
    message = ""
    end = time.time()
    elapsed_time = end-start


    if "message" in string:
        print("Elapsed: ", elapsed_time)
        if elapsed_time < 5:
            sendmessage(IP, "You need to wait 5 seconds before sending another command.")
        else:
            packet_type = string.split(",")[2].strip()
            message = string.split(",")[3].strip()
            rssi = int(string.split(",")[4].strip())
            if "rm" == message[:2]:
                sendmessage(IP, "You can not execute remove commands.")
            else:
                if RSSI == 0:
                    RSSI = rssi

                print(RSSI, rssi)
                diff = abs(rssi - RSSI)
                if diff>10:
                    pass
                else:
                    print("New command: " + message)
                    command = message.split(" ")
                    output = ""
                    try:
                        output = subprocess.check_output(command).decode("utf-8")
                    except Exception as e:
                        output = str(e)

                    sendmessage(IP, output)

    #response packet
    else:

        packet_type = string.split(",")[2].strip()
        if [username , IP] not in Online_Users:
            Online_Users.append([username , IP])

        print("\n")
        print("#####################")
        print("Quick Notification : ")
        print(username + " is online")
        print("#####################")
        print("\n")
        print("Please continue to write your instruction or command below")


def broadcast(sock,packet):

    global PORT

    sock.sendto(packet,( '<broadcast>', PORT))

def announce():

    global PORT
    global Local_IP
    global name


    packet = "[" + name + ", " + Local_IP + ", " + "announce" + "]" 
    packet = packet.encode('ascii' , 'replace')

    while True :

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        count = 0

        # Send 3 broadcast packets
        while count<3 :

            start_new_thread(broadcast,(sock,packet))
            #sock.sendto(packet , ( '<broadcast>', PORT))

            #sleep 0.25 seconds between packets
            count = count +1
            time.sleep(0.25)

        sock.close()
        time.sleep(10)

def sendmessage(ip, text):

    global Local_IP
    global name,start

    printOnlineUsers()

    message = text
    packet = "[" + name + ", " + Local_IP + ", " + "message" + ", " + message + "]"

    start_new_thread(send_packet,(ip , packet))

    start = time.time()


def printOnlineUsers():

    global Online_Users

    print("#####################")
    print("ONLINE USERS : ")
    
    for user in Online_Users:
        print("Name is : " + user[0] + " , " + "IP of " + user[0] + " : " + user[1])
    
    print("#####################")


def myProfile():

    global PORT
    global Local_IP
    global Local_NET
    global name

    print("#####################")
    print("MY PROFİLE : ")
    print("Username : " + name)
    print("Local IP : " + Local_IP)
    print("Local NET : "+ Local_NET)
    print("PORT : " + str(PORT))
    print("#####################")

def quit_app():

    subprocess.call(["pkill", "-f" , "zeroconf.py"])

def commands():

    print("#####################")
    print("AVAILABLE COMMANDS")
    print("#####################")

    commands = ["0)List online users" , "1)Show my profile" , "2)Send message" , "3)Quit"]

    for command in commands :
        print(command)

    print("In order to List online users , type 0")
    print("In order to Show my profile , type 1")
    print("In order to Send message , type 2")
    print("In order to Quit , type 3")

    command = input("Enter your command  : ") 

    if command == "0" :
        printOnlineUsers()
    elif command == "1" :
        myProfile()
    elif command == "2" :
        sendmessage()
    elif command == "3":
        quit_app()  
    else :
        print("Invalid command")




announce_thread = threading.Thread(target = announce , args=())
announce_thread.setDaemon(True)
announce_thread.start()

listen_thread = threading.Thread(target= listen_broadcast , args=())
listen_thread.setDaemon(True)
listen_thread.start()

listen_packets_thread = threading.Thread(target= listen_TCP_packets , args=())
listen_packets_thread.setDaemon(True)
listen_packets_thread.start()


while True:

    commands()
    time.sleep(0.5)



