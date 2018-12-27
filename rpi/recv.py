#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import socket
import struct
import threading
import time
import atexit

#connect to server
HOST = '192.168.1.15'    # The remote host
PORT = 5000             # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("",PORT))

address = (HOST, PORT)
#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
try: 
   s.sendto("HELLO".encode(),address)
   print("connected to "+HOST)
except Exception as e:
   print("server not available" + str(e.args))
   pass

mh = Adafruit_MotorHAT(addr=0x60)
# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
   mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
   mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
   mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
   mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)
LMotor = mh.getMotor(3)
RMotor = mh.getMotor(1)
   

RMotor.run(Adafruit_MotorHAT.FORWARD)
LMotor.run(Adafruit_MotorHAT.BACKWARD)
                

def process_msg(data):
    # Move motors at power sent from server
    print(data.decode())
    power = data.decode().split(';')
    power[0] = int(power[0])/3
    power[1] = int(power[1])/3
    LMotor.setSpeed(power[0])
    RMotor.setSpeed(power[1])
    
while True:
         # recieve messages from server
         data = ''
         try: 
            indata = s.recvfrom(1500)
            print(indata)
            data,tmp = indata
            process_msg(data)
         except Exception as e:
            print("FAILURE TO RECV.." + str(e.args) + "..RECONNECTING")
            try:
               s.close()
               s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
               s.bind(("",PORT))
               print("connected to "+HOST)
            except:
               pass
