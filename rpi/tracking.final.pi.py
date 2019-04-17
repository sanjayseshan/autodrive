# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time,sys
import cv2

import numpy as np
import struct
import socket
import random

# set up network socket/addresses
host = 'localhost'
Lport = 4000
Rport = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", Lport))
print ("Active on port: " + str(Lport))
robot_address = (host, Rport)

# initialize the camera
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320, 240))
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
# allow the camera to warmup
time.sleep(0.1)
xdim = 320
ydim = 240
cropsize = 80
gmax=0
rmax=0
lastP_fix = 0
I_fix=0
lower_black=np.array([0,0,0])
upper_black=np.array([180,125,80])

interval = sys.argv[1]
update = sys.argv[1]
#interval = random.randint(1, 10)
duration = sys.argv[2]
threshold = int(sys.argv[3])

def SendToRobot(left, right, error, P, I, D):
    global sock
    data = str(left)+";"+str(right)+";"+str(error)+";"+str(P)+";"+str(I)+";"+str(D)
    send_msg = str(str(data)).encode()
    try:
          sock.sendto(send_msg, robot_address)
          #print send_msg
    except Exception as e:
          print("FAIL - RECONNECT.." + str(e.args))
          try:
                  print("sending " + send_msg)
                  sock.sendto(send_msg, robot_address)
          except:
                  print("FAILED.....Giving up :-(")

def FindColor(imageHSV, lower_col, upper_col, min_area):
    # find the colored regions
    mask=cv2.inRange(imageHSV,lower_col,upper_col)
#    cv2.imshow("mask",mask)

    # this removes noise by eroding and filling in
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    conts, h = cv2.findContours(maskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Finding bigest  area and save the contour
    max_area = 0
    for cont in conts:
        area = cv2.contourArea(cont)
        if area > max_area:
            max_area = area
            gmax = max_area
            best_cont = cont
    # identify the middle of the biggest  region
    if conts and max_area > min_area:
        M = cv2.moments(best_cont)
        cx,cy = int(M['m10']/M['m00']),int(M['m01']/M['m00'])
        return best_cont, cx, cy, max_area
    else:
        return 0,-1,-1,-1


lastTime = time.time()
#interval = 0.4



colors = []

def on_mouse_click (event, x, y, flags, frame):
    global thiscol,lower_green,upper_green,lower_red,upper_red,lower_black,upper_black
    if event == cv2.EVENT_LBUTTONUP:
        colors.append(frame[y,x].tolist())
        print(thiscol)
        print(frame[y,x].tolist())

        if thiscol == "black":
            lower_black=np.array([frame[y,x].tolist()[0]-255,frame[y,x].tolist()[1]-100,frame[y,x].tolist()[2]-100])
            upper_black=np.array([frame[y,x].tolist()[0]+255,frame[y,x].tolist()[1]+50,frame[y,x].tolist()[2]+50])
            thiscol = "none"

thiscol = "black"

#def main():
#global thiscol
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        cap_img = frame.array
        full_img = cap_img
        img=cv2.resize(cap_img,(xdim,ydim))
        orig_img = img.copy()
#        hsv = img
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        if thiscol == "black":
            cv2.putText(img, str("CLICK ON BLACK"), (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (20, 255, 255), 2)            
        if colors:
            cv2.putText(img, str(colors[-1]), (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (20, 255, 255), 2)
        cv2.imshow('frame', img)
        cv2.setMouseCallback('frame', on_mouse_click, hsv)

    	rawCapture.truncate(0)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if thiscol == "none":
                break

cv2.destroyAllWindows()





for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    if (time.time()-lastTime) > float(interval):
        lastTime = time.time()
        randval = random.randint(1, 100)
        #print randval
        if (randval < threshold):
            time.sleep(float(interval))
            print("P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())
            SendToRobot(0,0,0,0,0,0)

    cv2.imshow("robotimgPi", full_img)

    cap_img = frame.array
    full_img = cap_img
    #full_img=cv2.resize(cap_img,(xdim,ydim))
#    cv2.imshow("1",full_img)

    imgHSV = cv2.cvtColor(full_img,cv2.COLOR_BGR2HSV)
    imgHSV_crop = imgHSV[200:280, 0:320]

    key = cv2.waitKey(1) & 0xFF

    best_blackcont, blackcx_incrop, blackcy_incrop, blackarea = FindColor(imgHSV_crop, lower_black, upper_black, 10)


    rawCapture.truncate(0)

    if (blackcx_incrop == -1):
        # if robot not found --> done
        print("P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())
        SendToRobot(0,0,0,0,0,0)
        continue

    #ctr = full_img.copy()
    #cv2.drawContours(ctr,best_blackcont+[0,200],-1,(0,255,0),3)
#    cv2.imshow("2",ctr)

    # create a rectangle to represent the line and find
    # the angle of the rectangle on the screen.
    blackbox = cv2.minAreaRect(best_blackcont)
    (x_min, y_min), (w_min, h_min), lineang = blackbox

    blackbox = (x_min, y_min+200), (w_min, h_min), lineang
    drawblackbox = cv2.cv.BoxPoints(blackbox)
    drawblackbox = np.int0(drawblackbox)
    cv2.drawContours(full_img,[drawblackbox],-1,(0,255,0),3)
#    cv2.imshow("3",full_img)

    # draw line with the estimate of location and angle
    cv2.line(full_img, (int(x_min),int(y_min+200)), (160,40+200), (200,0,200),2)
    cv2.circle(full_img,(int(x_min),int(y_min+200)),3,(200,0,200),-1)
    deltaX = 0.333*(160-x_min)


    P_fix = deltaX
    I_fix = P_fix+0.9*I_fix
    D_fix = P_fix-lastP_fix
    lastP_fix = P_fix
    error = 100*blackarea/5500
    print("P, I, D, (E), (T) --->", P_fix, I_fix, D_fix, error, time.time())

    kP = 1.5
    kI = 0.15
    kD = 4.5
    
    # Compute correction based on angle/position error
    left = int(100 - kP*P_fix - kD*D_fix - kI*I_fix)
    right = int(100 + kP*P_fix + kD*D_fix + kI*I_fix)

    SendToRobot(left,right,error, P_fix, I_fix, D_fix)


    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
    	break
