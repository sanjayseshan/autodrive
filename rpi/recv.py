#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import socket
import struct
import time
import atexit

HOST = '192.168.1.17' # The remote host
PORT = 5000 # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("",PORT))

address = (HOST, PORT)

cam0=[0,0,0]
cam1=[0,0,0]
picam=[0,0,0]
piout="0,0,0,0,0,0"
cam0out="0,0,0,0,0,0"
cam1out="0,0,0,0,0,0"

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
print(str("time,left,right,piLeft,piRight,piConf,piP,piI,piD,cam0Left,cam0Right,cam0Conf,cam0P,cam0I,cam0D,cam1Left,cam1Right,cam1Conf,cam1P,cam1I,cam1D"))

while True:
    # receive messages from server
    data = ''
    try:
        indata = s.recvfrom(1500)
        #print indata
        data,tmp = indata
        ip,port=tmp
        message = data.decode().split(';')
        left = int(message[0])/3.0
        message[0] = left
        right = int(message[1])/3.0
        message[1] = right
        confidence = float(message[2])/3.0
        message[2] = confidence
        message[3] = float(message[3])
        message[4] = float(message[4])
        message[5] = float(message[5])

        if ip == "127.0.0.1":
           piout = str(message[0])+","+str(message[1])+","+str(message[2])+","+str(message[3])+","+str(message[4])+","+str(message[5])
           if left > 0 or right > 0:
              picam = message
           else:
              picam = [0,0,0,0,0,0]

        elif ip == "192.168.1.17" and port == 4000:
           cam0out = str(message[0])+","+str(message[1])+","+str(message[2])+","+str(message[3])+","+str(message[4])+","+str(message[5])
           if left > 0 or right > 0:
              cam0 = message
           else:
              cam0 = [0,0,0,0,0,0] # why???
        elif ip == "192.168.1.17" and port == 4001:
           cam1out = str(message[0])+","+str(message[1])+","+str(message[2])+","+str(message[3])+","+str(message[4])+","+str(message[5])
           if left > 0 or right > 0:
              cam1 = message
           else:
              cam1 = [0,0,0,0,0,0] # why???

        # Move motors at power sent from server
        avgpower = [int((picam[2]*picam[0]+cam0[2]*cam0[0]+cam1[2]*cam1[0])/(picam[2]+cam0[2]+cam1[2])),int((picam[2]*picam[1]+cam0[2]*cam0[1]+cam1[2]*cam1[1])/(picam[2]+cam0[2]+cam1[2]))]
#        print("L: "+str(avgpower[0])+" R: "+str(avgpower[1]) + " T: " + str(time.time()))
        print(str(time.time())+","+str(avgpower[0])+","+str(avgpower[1]) + "," +str(piout)+","+str(cam0out)+","+str(cam1out))
        LMotor.setSpeed(avgpower[0])
        RMotor.setSpeed(avgpower[1])
    except Exception as e:
        #print("L: "+str(0)+" R: "+str(0) + " T: " + str(time.time()))
        print(str(time.time())+","+str(avgpower[0])+","+str(avgpower[1]) + "," +str(piout)+","+str(cam0out)+","+str(cam1out)+",-1")
#        print(str(time.time())+","+str(0)+","+str(0) + "," +str(0)+","+str(0)+","+str(0))
        try:
           s.close()
           s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
           s.bind(("",PORT))
        except:
           pass
