import cv2
import numpy as np
import time
import os
import socket
import struct
from time import sleep
import sys
import time
import math
import random

# set up network socket/addresses
host = '192.168.1.5'
Lport = 4000+int(sys.argv[1])
Rport = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", Lport))
print ("Active on port: " + str(Lport))
robot_address = (host, Rport)

# set up camera
camid=sys.argv[1]
cam = cv2.VideoCapture(int(camid))
print("init camera on /dev/video"+sys.argv[1])

#set up opencv variables
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
font=cv2.FONT_HERSHEY_PLAIN
xdim = 1280
ydim = 720
cropsize = 75
gmax=0
rmax=0
lastP_fix = 0
I_fix=0
colors = []
thiscol = "green"

#interval = sys.argv[2]
update = sys.argv[2]
interval = random.randint(1, 10)
duration = sys.argv[3]

def on_mouse_click (event, x, y, flags, frame):
    global thiscol,lower_green,upper_green,lower_red,upper_red
    if event == cv2.EVENT_LBUTTONUP:
        colors.append(frame[y,x].tolist())
        print(thiscol)
        print(frame[y,x].tolist())
        if thiscol == "green":
            lower_green=np.array([frame[y,x].tolist()[0]-20,frame[y,x].tolist()[1]-30,frame[y,x].tolist()[2]-50])
            upper_green=np.array([frame[y,x].tolist()[0]+20,frame[y,x].tolist()[1]+30,frame[y,x].tolist()[2]+50])
            thiscol = "red"
        elif thiscol == "red":
            lower_red=np.array([frame[y,x].tolist()[0]-20,frame[y,x].tolist()[1]-30,frame[y,x].tolist()[2]-50])
            upper_red=np.array([frame[y,x].tolist()[0]+20,frame[y,x].tolist()[1]+30,frame[y,x].tolist()[2]+50])
            thiscol = "none"

def calibrate():
    capture = cv2.VideoCapture(camid)
    global thiscol,lower_black,upper_black
    lower_black=np.array([0,0,0])
    upper_black=np.array([180,125,80])
    while thiscol != "none":
        ret, cap_img=cam.read()
        img=cv2.resize(cap_img,(xdim,ydim))
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        cv2.putText(img, str("CLICK ON " + thiscol), (10, 50), font, 2, (0, 0, 0), 2)
        if colors:
            cv2.putText(img, "LAST: "+str(colors[-1]), (10, 100), font, 2, (0, 0, 0), 2)
        cv2.imshow('frame', img)
        cv2.setMouseCallback('frame', on_mouse_click, hsv)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    cv2.destroyAllWindows()

def FindColor(imageHSV, lower_col, upper_col, min_area, col):
    # find the colored regions
    mask=cv2.inRange(imageHSV,lower_col,upper_col)
#    cv2.imshow(col,mask)

    # this removes noise by eroding
    # and filling in the regions
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    conts, h = cv2.findContours(maskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Finding bigest area and save the contour
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
        cx,cy=int(M['m10']/M['m00']),int(M['m01']/M['m00'])
        return best_cont, cx, cy, max_area
    else:
        return 0,-1,-1,-1

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

def ComputeRobotAngle(greencx, greency, redcx, redcy):
    # find the angle from the center of green to center
    # of red this is the angle of the robot in the image
    # I need to special case of 90/-90 due to tan()
    # discontinuity I also need to deal with angles > 90
    # and < 0 to map correctly to a 360 degree circle
    if (greencx-redcx) == 0:
        if greency > redcy:
            ang = 90
        else:
            ang = 270
    else:
        Tredcy = ydim - redcy
        Tgreency = ydim - greency
        ang = 180/np.pi * np.arctan(float(redcy-greency)/float(redcx-greencx))
        if greencx > redcx:
            ang = 180 + ang
        elif ang < 0:
            ang = 360 + ang
        ang = 360-ang
    return ang


calibrate()
lastTime = time.time()
threshold = 0.4

while True:
 try:
    cv2.waitKey(10)
    if (time.time()-lastTime) > float(interval):
        lastTime = time.time()
        if (random.randint(1, 100) < threshold):
            time.sleep(float(interval))
            print("P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())
            SendToRobot(0,0,0,0,0,0)
            
    try:
        cv2.putText(img, "green: "+str(colors[0]), (10, 50), font, 2, (0, 0, 0), 2)
        cv2.putText(img, "orange: "+str(colors[1]), (10, 80), font, 2, (0, 0, 0), 2)
        cv2.imshow("robotimg"+camid,img)
    except:
        pass

    # grab image, resize, save a copy and convert to HSV
    ret, cap_img=cam.read()
    img=cv2.resize(cap_img,(xdim,ydim))
#    cv2.imshow("1",img)
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    # find largest green region
    best_greencont, greencx, greency, greenarea = FindColor(imgHSV, lower_green, upper_green, 3000, "green")
    if (greencx == -1):
        # if robot not found --> done
        print("ng P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())
        SendToRobot(0,0,0,0,0,0)
        continue

    cv2.drawContours(img,best_greencont,-1,(0,255,0),3)

    # crop frame to be around robot only
    robotimgHSV = imgHSV[max(greency-200,0):greency+200,max(greencx-300,0):greencx+300]

    # find red region in this cropped area
    best_redcont, redcx_incrop, redcy_incrop, redarea = FindColor(robotimgHSV, lower_red, upper_red, 3000, "red")
    if (redcx_incrop == -1):
        # if robot not found --> done
        print("nr P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())
        SendToRobot(0,0,0,0,0,0)
        continue

    redcx = redcx_incrop+max(greencx-300,0);
    redcy = redcy_incrop+max(greency-200,0);
    cv2.drawContours(img, best_redcont+[max(greencx-300,0),max(greency-200,0)], -1, (0,255,0), 3)
    #cv2.imshow("2",img)

    ang=ComputeRobotAngle(greencx,greency,redcx,redcy)

    # draw some robot lines on the screen and display
    cv2.line(img, (greencx,greency), (redcx,redcy), (200,0,200),3)
    cv2.putText(img, "robot ang: "+str(ang), (10, 160), font, 2, (0, 0, 0), 2)
    #cv2.imshow("3",img)

    # find a small region in front of the robot and
    # crop that part of the image
    ylen = (greency-redcy)
    xlen = (greencx-redcx)
    boxX = redcx - xlen/2
    boxY = redcy - ylen/2
    if boxX > (xdim-cropsize):
        Xcropsize = xdim - boxX
    elif boxX < cropsize:
        Xcropsize = boxX
    else:
        Xcropsize = cropsize

    if boxY > (ydim-cropsize):
        Ycropsize = ydim - boxY
    elif boxY < cropsize:
        Ycropsize = boxY
    else:
        Ycropsize = cropsize

    if (Xcropsize > 0) and (Ycropsize > 0):
        lineimgHSV = imgHSV[int(abs(boxY-Ycropsize)):int(abs(boxY+Ycropsize)), int(abs(boxX-Xcropsize)):int(abs(boxX+Xcropsize))]
        # find black region in cropped area
        best_blackcont, blackcx_incrop, blackcy_incrop, blackarea = FindColor(lineimgHSV, lower_black, upper_black, 200, "black")
    else:
        blackcx_incrop = -1

    if (blackcx_incrop == -1):
        # skip if didn't find a line
        print("nb P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())
        SendToRobot(0,0,0,0,0,0)
        continue

    blackcx = blackcx_incrop+int(abs(boxX-Xcropsize))
    blackcy = blackcy_incrop+int(abs(boxY-Ycropsize))

    # create a rectangle to represent the line and find
    # the angle of the rectangle on the screen.
    blackbox = cv2.minAreaRect(best_blackcont)
    (x_min, y_min), (w_min, h_min), lineang = blackbox

    # draw box on screen
    x_min_real = x_min + int(abs(boxX-Xcropsize))
    y_min_real = y_min + int(abs(boxY-Ycropsize))
    blackbox = (x_min_real, y_min_real), (w_min, h_min), lineang
    drawblackbox = cv2.boxPoints(blackbox)
    drawblackbox = np.int0(drawblackbox)
    cv2.drawContours(img,[drawblackbox],0,(0,255,0),3)
    cv2.imshow("4",lineimgHSV)

    # Unfortunately, opencv only gives rectangles angles
    # from 0 to -90 so we need to do some guesswork to
    # get the right quadrant for the angle
    if w_min > h_min:
        if (ang > 135):
            lineang = 180 - lineang
        else:
            lineang = -1 * lineang
    else:
        if (ang > 270) or (ang < 45):
            lineang = 270 - lineang
        else:
            lineang = 90 - lineang

    # draw estimate of line location and angle
    x_end = int(x_min_real-50*np.cos(lineang*np.pi/180))
    y_end = int(y_min_real+50*np.sin(lineang*np.pi/180))
    cv2.line(img, (int(x_min_real),int(y_min_real)), (x_end,y_end), (200,0,200),2)
    cv2.circle(img,(int(x_min_real),int(y_min_real)),3,(200,0,200),-1)
    cv2.line(img, (int(x_min_real),int(y_min_real)), (boxX,boxY), (200,0,200),2)
    cv2.putText(img, "line ang: "+str(lineang), (10, 190), font, 2, (0, 0, 0), 2)
    #cv2.imshow("5",img)

    # The direction error is the difference in angle of
    # the line and robot essentially the derivative in
    # a PID controller
    D_fix = lineang - ang
    if D_fix < -300:
        D_fix += 360
    elif D_fix > 300:
        D_fix -= 360


    # the line angle guesswork is sometimes off by 180
    # degrees. detect and fix this error here
    if D_fix < -90:
        D_fix += 180
    elif D_fix > 90:
        D_fix -= 180
    cv2.putText(img, "D_fix: "+str(D_fix), (10, 300), font, 2, (0, 0, 0), 2)

    # the position error is an estimate of how far the
    # front center of the robot is from the line. The
    # center of the cropped image
    # (x,y) = (cropsize, cropsize) is the front of the
    # robot. (x_min, y_min) is the center of the line.
    # Draw a line from the front center of the robot
    # to the center of the line. Difference in angle
    # between this line and robot's direction is the
    # position error.
    if (x_min - cropsize) == 0:
        if (ang < 180):
            P_fix = 90 - ang
        else:
            P_fix = 270 - ang
    else:
        temp_angle = 180/np.pi * np.arctan(float(Ycropsize - y_min)/float(x_min - Xcropsize))
        if (temp_angle < 0):
            if (ang > 225):
                temp_angle = 360 + temp_angle
            else:
                temp_angle = 180 + temp_angle
        elif (ang > 135 and ang < 315):
                temp_angle = 180 + temp_angle
        P_fix = temp_angle - ang
    if (P_fix > 180):
        P_fix = P_fix - 360
    elif P_fix < -180:
        P_fix = 360 + P_fix
    # the line angle guesswork is sometimes off by 180
    # degrees. Detect and fix this error here
    if P_fix < -90:
        P_fix += 180
    elif P_fix > 90:
        P_fix -= 180
    cv2.putText(img, "center angle: "+str(temp_angle), (10, 220), font, 2, (0, 0, 0), 2)
    cv2.putText(img, "P_fix: "+str(P_fix), (10, 330), font, 2, (0, 0, 0), 2)

    # Integral controller is just the sum of the P_fix
    # with an exponential decay rate of 0.5
    I_fix = P_fix + 0.5*I_fix

    lastP_fix = P_fix

    # print and save correction and current network conditions
    error = 100*blackarea/1300
    print("P, I, D, (E), (T) --->", P_fix, I_fix, D_fix, error, time.time())

    # Compute correction based on angle/position error
    left = int(100 - 1.0*P_fix - .5*D_fix - 0.02*I_fix)
    right = int(100 + 1.0*P_fix + .5*D_fix + 0.02*I_fix)

    # send movement fix to robot
    SendToRobot(left,right,error, P_fix, I_fix, D_fix)
 except:
     pass
