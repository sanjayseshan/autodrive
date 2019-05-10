import ev3dev.ev3 as ev3
import socket
import struct
import threading
import time

#Basic motor setup
B = ev3.LargeMotor('outB')
C = ev3.LargeMotor('outC')

#connect to server with TCP
HOST = '192.168.1.18'    # The remote host
PORT = 5000             # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = (HOST, PORT)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
try:
   s.connect((HOST, PORT))
   print("connected to "+HOST)
except Exception as e:
   print("server not available" + str(e.args))
   pass


def process_msg(data):
    # set motor power at what was sent by server
    print(data.decode())
    power = data.decode().split(';')
    power[0] = float(power[0])
    power[1] = float(power[1])
    B.run_forever(speed_sp=power[0])
    C.run_forever(speed_sp=power[1])

while True:
         #recieve data from server
         data = ''
         try:
            data,tmp = s.recv(1500)
            process_msg(data)
         except Exception as e:
            print("FAILURE TO RECV.." + str(e.args) + "..RECONNECTING")
            try:
               s.close()
               s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
               s.connect((HOST, PORT))
               print("connected to "+HOST)
            except:
               pass
