#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import socket
import struct
import threading
import time
import atexit

#connect to server
HOST = '192.168.1.30'    # The remote host
PORT = 5000             # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("",PORT))

address = (HOST, PORT)

cam0=[0,0]
cam1=[0,0]
picam=[0,0]

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
                


    
while True:
         # recieve messages from server
         data = ''
         try: 
            indata = s.recvfrom(1500)
            print(indata)
            data,tmp = indata
            ip,port=tmp
            power = data.decode().split(';')
            print(ip+":"+str(port)+" --> "+data.decode())
            power[0] = int(power[0])/3
            power[1] = int(power[1])/3
            if ip == "127.0.0.1":
               if power[0] > 0 or power[1] > 0:
                  picam = power
               else:
                  picam = cam0
            elif ip == "192.168.1.30" and port == 4000:
               if power[0] > 0 or power[1] > 0:
                  cam0 = power
               else:
                  cam0 = picam
            elif ip == "192.168.1.30" and port == 4001:
               if power[0] > 0 or power[1] > 0:
                  cam1 = power
               else:
                  cam1 = cam0
               # Move motors at power sent from server
            avgpower = [(2*picam[0]+cam0[0]+cam1[0])/4,(2*picam[1]+cam0[1]+cam1[1])/4]
            print("L: "+str(avgpower[0])+" R: "+str(avgpower[1]))
            LMotor.setSpeed(avgpower[0])
            RMotor.setSpeed(avgpower[1])
         except Exception as e:
            print("FAILURE TO RECV.." + str(e.args) + "..RECONNECTING")
            try:
               s.close()
               s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
               s.bind(("",PORT))
               print("connected to "+HOST)
            except:
               pass
