import cv2
import numpy as np
import time
import os
import socket
import struct
from time import sleep
import sys
import time

# set up network socket/addresses
host = '192.168.1.19'
Lport = 4000+int(sys.argv[1])
Rport = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", Lport))
print ("Active on port: " + str(Lport))
robot_address = (host, Rport)

print("init camera on /dev/video"+sys.argv[1])

lower_red2 = np.array([160,200,100])
upper_red2 = np.array([180,255,255])
"""
# set up robot colors
if sys.argv[1] == "0" or sys.argv[1] == "1": # for new Logitech camera
    lower_green=np.array([35,60,50])
    upper_green=np.array([105,220,140])
    lower_black=np.array([0,0,0])
    upper_black=np.array([200,60,60])
    lower_red = np.array([0,100,100])
    upper_red = np.array([60,255,255])
    lower_red2 = np.array([160,200,100])
    upper_red2 = np.array([180,255,255])
    lower_blue = np.array([85,31,63])
    upper_blue = np.array([138,106,127])
    lower_orange = np.array([0,120,120])
    upper_orange = np.array([40,255,255])

    # set up camera
    cam = cv2.VideoCapture(int(sys.argv[1]))
else: # for old Logitech camera
    lower_green=np.array([75,60,50])
    upper_green=np.array([105,220,140])
    lower_black=np.array([0,0,0])
    upper_black=np.array([180,90,90])
    lower_red = np.array([0,100,100])
    upper_red = np.array([20,255,255])
    lower_red2 = np.array([160,100,100])
    upper_red2 = np.array([180,255,255])
    lower_blue = np.array([85,31,63])
    upper_blue = np.array([138,106,127])
    lower_orange = np.array([0,120,120])
    upper_orange = np.array([40,255,255])
"""
    # set up camera
cam = cv2.VideoCapture(int(sys.argv[1]))

#set up opencv variables
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
font=cv2.FONT_HERSHEY_SIMPLEX
xdim = 1280
ydim = 720
cropsize = 100
gmax=0
rmax=0
lastP_fix = 0
I_fix=0

camid=sys.argv[1] # which camera is used --> simply an identification method




colors = []

def on_mouse_click (event, x, y, flags, frame):
    global thiscol,lower_green,upper_green,lower_red,upper_red,lower_black,upper_black
    if event == cv2.EVENT_LBUTTONUP:
        colors.append(frame[y,x].tolist())
        print(thiscol)
        print(frame[y,x].tolist())
        if thiscol == "green":
            lower_green=np.array([frame[y,x].tolist()[0]-20,frame[y,x].tolist()[1]-20,frame[y,x].tolist()[2]-20])
            upper_green=np.array([frame[y,x].tolist()[0]+20,frame[y,x].tolist()[1]+20,frame[y,x].tolist()[2]+20])
            thiscol = "red"
        elif thiscol == "red":
            lower_red=np.array([frame[y,x].tolist()[0]-20,frame[y,x].tolist()[1]-20,frame[y,x].tolist()[2]-20])
            upper_red=np.array([frame[y,x].tolist()[0]+20,frame[y,x].tolist()[1]+20,frame[y,x].tolist()[2]+20])
            thiscol = "black"
        elif thiscol == "black":
            lower_black=np.array([frame[y,x].tolist()[0]-255,frame[y,x].tolist()[1]-100,frame[y,x].tolist()[2]-100])
            upper_black=np.array([frame[y,x].tolist()[0]+70,frame[y,x].tolist()[1]+20,frame[y,x].tolist()[2]+20])
            thiscol = "none"
thiscol = "green"

def main():
    capture = cv2.VideoCapture(camid)
    global thiscol
    while thiscol != "none":
        ret, cap_img=cam.read()
        img=cv2.resize(cap_img,(xdim,ydim))
        orig_img = img.copy()
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        if thiscol == "green":
            cv2.putText(img, str("CLICK ON GREEN"), (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        if thiscol == "red":
             cv2.putText(img, str("CLICK ON ORANGE"), (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        if thiscol == "black":
            cv2.putText(img, str("CLICK ON BLACK"), (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            
        if colors:
            cv2.putText(img, str(colors[-1]), (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        cv2.imshow('frame', img)
        cv2.setMouseCallback('frame', on_mouse_click, hsv)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

main()
    
while True:
    cv2.waitKey(10)
    
    # grab image, resize, save a copy and convert to HSV
    ret, cap_img=cam.read()
    img=cv2.resize(cap_img,(xdim,ydim))
    orig_img = img.copy()
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    #cv2.imshow("cam_raw"+camid,img)

    # identify the green regions --> estimates the position of the robot
    greenmask=cv2.inRange(imgHSV,lower_green,upper_green)
    # this removes noise by eroding and filling in the regions
    greenmaskOpen=cv2.morphologyEx(greenmask,cv2.MORPH_OPEN,kernelOpen)
    greenmaskClose=cv2.morphologyEx(greenmaskOpen,cv2.MORPH_CLOSE,kernelClose)
    greenconts, h = cv2.findContours(greenmaskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Finding bigest green area and save the contour
    max_area = 0
    for cont in greenconts:
        area = cv2.contourArea(cont)
        if area > max_area:
            max_area = area
            gmax = max_area
            best_greencont = cont
    greencx,greency = (300,200)
    # identify the middle of the biggest green region
    if greenconts and max_area > 5000:
        cv2.drawContours(img, best_greencont, -1, (0,255,0), 3)
        M = cv2.moments(best_greencont)
        greencx,greency = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        #print greencx
 #   cv2.imshow("cam_contg"+camid,img)

    # crop frame to be around robot only        
    robotimg = imgHSV[max(greency-200,0):greency+200,max(greencx-300,0):greencx+300] 

    # identify the red regions - red is tricky sine it is both 170-180 and 0-10
    # in the hue range
    redmask0 = cv2.inRange(robotimg, lower_red, upper_red)
    redmask1 = cv2.inRange(robotimg, lower_red2, upper_red2)
    redmask = redmask0 + redmask1
#    print lower_red
#    print upper_red
#    cv2.imshow("red2",redmask0)
#    cv2.imshow("robotimg",robotimg)
    # this removes noise by eroding and filling in the regions
    redmaskOpen=cv2.morphologyEx(redmask,cv2.MORPH_OPEN,kernelOpen)
    redmaskClose=cv2.morphologyEx(redmaskOpen,cv2.MORPH_CLOSE,kernelClose)
    redconts, h = cv2.findContours(redmaskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Finding bigest red area and save the contour
    max_area = 0
    for cont in redconts:
        area = cv2.contourArea(cont)
        if area > max_area:
            max_area = area
            rmax = max_area
            best_redcont = cont
            
    # identify the middle of the biggest red region
    if redconts and max_area > 5000:
        #print [greencx-300,greency]
        #print  best_redcont+[max(greencx-300,0),max(greency-200,0)]
        cv2.drawContours(img, best_redcont+[max(greencx-300,0),max(greency-200,0)], -1, (0,255,0), 3)
        M = cv2.moments(best_redcont)
        redcx,redcy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    #cv2.imshow("red",img)

    if not (redconts and greenconts and gmax > 5000 and rmax > 5000):
        # if robot not found --> done
        data = str(0) + ";" + str(0) + ";" + str(0)
        print("P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())


        # send movement fix to robot
        send_msg = str(str(data)).encode()
        try:
            sock.sendto(send_msg, robot_address)
        except Exception as e:
            print("FAILURE TO SEND.." + str(e.args) + "..RECONNECTING")
            try:
                print("sending " + send_msg)
                sock.sendto(send_msg, robot_address)
            except:
                print("FAILED.....Giving up :-( - pass;")
        continue

    # find the angle from the center of green to center of red
    # this is the angle of the robot in the image
    # I need to special case of 90/-90 due to tan() discontinuity
    # I also need to deal with angles > 90 and < 0 to map correctly
    # to a 360 degree circle
    if (greencx-(redcx+max(greencx-300,0))) == 0:
        if greency > redcy+max(greency-200,0):
            ang = 90
        else:
            ang = 270
    else:
        Tredcy = ydim - (redcy+max(greency-200,0))
        Tgreency = ydim - greency
        ang = 180/np.pi * np.arctan((Tredcy-Tgreency)/((redcx+max(greencx-300,0))-greencx))
        if greencx > redcx+max(greencx-300,0):
            ang = 180 + ang
        elif ang < 0:
            ang = 360 + ang

    # draw some robot lines on the screen and display
    cv2.line(img, (greencx,greency), (redcx+max(greencx-300,0),redcy+max(greency-200,0)), (200,0,200),3)
    cv2.imshow("robotimg",robotimg)

    #cv2.imshow("cam"+camid,img)

    # find a small region in front of the robot and crop that part of the image
    ylen = (greency-(redcy+max(greency-300,0)))
    xlen = (greencx-(redcx+max(greencx-300,0)))
    boxX = (redcx+max(greencx-300,0)) - xlen/1.6
    boxY = (redcy+max(greency-200,0)) - ylen/1.6
    
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
    
    crop_img = img[int(abs(boxY-Ycropsize)):int(abs(boxY+Ycropsize)), int(abs(boxX-Xcropsize)):int(abs(boxX+Xcropsize))]
    cv2.imshow("CROP",crop_img)
    # find the black regions in the cropped image (this is the line)
    blackmask=cv2.inRange(crop_img,lower_black,upper_black)
    blackmaskOpen=cv2.morphologyEx(blackmask,cv2.MORPH_OPEN,kernelOpen)
    blackmaskClose=cv2.morphologyEx(blackmaskOpen,cv2.MORPH_CLOSE,kernelClose)
    blackconts, h = cv2.findContours(blackmaskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #cv2.imshow("BLACK",blackmask)
    #print upper_black
    #print lower_black
    #Finding the largest black region
    max_area = 0
    for cont in blackconts:
        area = cv2.contourArea(cont)
        if area > max_area:
            #print area
            max_area = area
            best_blackcont = cont
    #print max_area
    if not (blackconts and max_area > 200):
        # skip if didn't find a line
        data = str(0) + ";" + str(0) + ";" + str(0)
        print("P, I, D, (E), (T) --->", 0, 0, 0, 0, time.time())


        # send movement fix to robot
        send_msg = str(str(data)).encode()
        try:
            sock.sendto(send_msg, robot_address)
        except Exception as e:
            print("FAILURE TO SEND.." + str(e.args) + "..RECONNECTING")
            try:
                print("sending " + send_msg)
                sock.sendto(send_msg, robot_address)
            except:
                print("FAILED.....Giving up :-( - pass;")
        continue

    # create a rectangle to represent the line and find
    # the angle of the rectangle on the screen.
    blackbox = cv2.minAreaRect(best_blackcont)
    drawblackbox = cv2.boxPoints(blackbox)
    drawblackbox = np.int0(drawblackbox)
    cv2.drawContours(crop_img,[drawblackbox],0,(0,255,0),3)
    (x_min, y_min), (w_min, h_min), lineang = blackbox
    # Unfortunately, opencv only gives rectangles angles from 0 to -90 so we
    # need to do some guesswork to get the right quadrant for the angle
    if w_min > h_min:
        if (ang > 135):
            lineang = 180 - lineang
        else:
            lineang = -1 * lineang
    else:
        if (ang > 225):
            lineang = 270 - lineang
        else:
            lineang = 90 - lineang

    # draw a line with the estimate of line location and angle
    cv2.line(crop_img, (int(x_min),int(y_min)), (int(x_min+50*np.cos(lineang*np.pi/180)),int(y_min-50*np.sin(lineang*np.pi/180))), (200,0,200),2)
    cv2.circle(crop_img,(int(x_min),int(y_min)),3,(200,0,200),-1)

    #try:
    #    cv2.imshow("boxlineangle"+camid, crop_img)
    #except:
    #    pass

    # The direction error is the difference in angle of the line and robot
    D_fix = lineang - ang
    # the line angle guesswork is sometimes off by 180 degrees. detect and
    # fix this error here
    # essentially the derivative in a PID controller
    if D_fix < -90:
        D_fix += 180
    elif D_fix > 90:
        D_fix -= 180

    # the position error is an estimate of how far the font center of the
    # robot is from the line. The center of the cropped image
    # (x,y) = (cropsize, cropsize) is the front of the robot. (x_min, y_min) is
    # the center of the line. Draw a line from the front center of the robot
    # to the center of the line. Difference in angle between this line and
    # robot's direction is the position error.
    if (x_min - cropsize) == 0:
        if (ang < 180):
            P_fix = 90 - ang
        else:
            P_fix = 270 - ang
    else:
        temp_angle = 180/np.pi * np.arctan((cropsize - y_min)/(x_min - cropsize))
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
    # the line angle guesswork is sometimes off by 180 degrees. Detect and
    # fix this error here
    if P_fix < -90:
        P_fix += 180
    elif P_fix > 90:
        P_fix -= 180

    I_fix = P_fix + 0.5*I_fix # Integral controller is just the sum of the P_fix with an exponential decay rate of 0.5

    lastP_fix = P_fix
    
    # print and save correction and current network conditions
    error = 100*max_area/1400
    print("P, I, D, (E), (T) --->", P_fix, I_fix, D_fix, error, time.time())
#    tmpos = os.popen('echo seshan | sudo -S tc qdisc show dev wlp7s0').read()
#    print(tmpos)

    # Compute correction based on angle/position error
    left = int(100 - 1*P_fix - 1*D_fix - 0.02*I_fix)
    right = int(100 + 1*P_fix + 1*D_fix + 0.02*I_fix)
    data = str(left) + ";" + str(right) + ";" + str(error)
    try:
        cv2.imshow("robotimg"+camid,img)
    except:
        pass
     # send movement fix to robot
    send_msg = str(str(data)).encode()
    try:
          sock.sendto(send_msg, robot_address)
          #print send_msg
    except Exception as e:
          print("FAILURE TO SEND.." + str(e.args) + "..RECONNECTING")
          try:
                  print("sending " + send_msg)
                  sock.sendto(send_msg, robot_address)
          except:
                  print("FAILED.....Giving up :-( - pass;")



