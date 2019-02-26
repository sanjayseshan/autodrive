# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time,sys
import cv2

import numpy as np
import struct
import socket

# set up network socket/addresses
host = 'localhost'
Lport = 4000
Rport = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", Lport))
print ("Active on port: " + str(Lport))
robot_address = (host, Rport)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

#lower_black=np.array([0,0,0])
#upper_black=np.array([200,60,60])
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
# allow the camera to warmup
time.sleep(0.1)
xdim = 320
ydim = 280
cropsize = 80
gmax=0
rmax=0
lastP_fix = 0
I_fix=0
# capture frames from the camera

colors = []

interval = sys.argv[1]
duration = sys.argv[2]

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

#main()

lastTime = time.time()
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
        print (time.time()-lastTime) 
        if (time.time()-lastTime) > float(interval):
            lastTime = time.time()
            print "Pausing"
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
            time.sleep(float(duration))

            
        cap_img = frame.array
 
	# show the frame
	#cv2.imshow("Frame", img)

        img=cv2.resize(cap_img,(xdim,ydim))
        full_img = img.copy()
        img = img[200:280, 0:320]
        #imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
	key = cv2.waitKey(1) & 0xFF

        blackmask=cv2.inRange(img,lower_black,upper_black)
        blackmaskOpen=cv2.morphologyEx(blackmask,cv2.MORPH_OPEN,kernelOpen)
        blackmaskClose=cv2.morphologyEx(blackmaskOpen,cv2.MORPH_CLOSE,kernelClose)
        blackconts, h = cv2.findContours(blackmaskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

	rawCapture.truncate(0)

        #Finding the largest black region
        max_area = 0
        for cont in blackconts:
                area = cv2.contourArea(cont)
                if area > max_area:
                        max_area = area
                        best_blackcont = cont
                #print best_blackcont

        if not blackconts:
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
        #cv2.imshow("CONTS",blackmask)
        cv2.drawContours(full_img,best_blackcont+[0,200],-1,(0,255,0),3)

        # create a rectangle to represent the line and find
        # the angle of the rectangle on the screen.
        #    cv2.drawContours(crop_img, best_blackcont, -1, (0,0,255), 3)
        blackbox = cv2.minAreaRect(best_blackcont)
        drawblackbox = cv2.cv.BoxPoints(blackbox)
        drawblackbox = np.int0(drawblackbox)
        #cv2.imshow("boxline",img)
        (x_min, y_min), (w_min, h_min), lineang = blackbox
        
        # Unfortunately, opencv only gives rectangles angles from 0 to -90 so we
        # need to do some guesswork to get the right quadrant for the angle
        """
        if w_min > h_min:
        lineang = 180 - lineang
        else:
        lineang = 270 - lineang
        print(lineang)
        """
        # draw a line with the estimate of line location and angle
        cv2.line(full_img, (int(x_min),int(y_min+200)), (160,40+200), (200,0,200),2)
        cv2.circle(full_img,(int(x_min),int(y_min+200)),3,(200,0,200),-1)
        deltaX = 0.333*(160-x_min)
        #print(deltaX)
        #cv2.line(img, (int(x_min),int(y_min)), (int(x_min+50*np.cos(lineang*np.pi/180)),int(y_min-50*np.sin(lineang*np.pi/180))), (200,0,200),2)
        #cv2.circle(img,(int(x_min),int(y_min)),3,(200,0,200),-1)
        
        #cv2.imshow("boxlineangle", img)
        cv2.imshow("robotimgPi", full_img)

        
        P_fix = deltaX
        I_fix = P_fix+0.5*I_fix
        D_fix = P_fix-lastP_fix
        lastP_fix = P_fix
        #print(max_area)
        error = 100*max_area/5500
        print("P, I, D, (E), (T) --->", P_fix, I_fix, D_fix, error, time.time())
        
        # Compute correction based on angle/position error
        left = int(100 - 1.5*P_fix - 1*D_fix - 0.01*I_fix)
        right = int(100 + 1.5*P_fix + 1*D_fix + 0.01*I_fix)
        data = str(left) + ";" + str(right) + ";" + str(error)

        # send movement fix to robot
        send_msg = str(str(data)).encode()
        try:
                sock.sendto(send_msg, robot_address)
        except Exception as e:
                prinxt("FAILURE TO SEND.." + str(e.args) + "..RECONNECTING")
                try:
                        print("sending " + send_msg)
                        sock.sendto(send_msg, robot_address)
                except:
                        print("FAILED.....Giving up :-( - pass;")
                        
	# clear the stream in preparation for the next frame
        
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
