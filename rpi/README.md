<h1>Raspberry Pi Code</h1>

tracking.final.pi.py: This is the code to run on the Raspberry Pi camera, which identifies the road and computes steering adjustment. 

<code>python tracking.final.pi.py <interval/duration> <null> <outage hreshold> </code>

recv.py: This is the code to run on the Raspberry Pi. It applies the transmittedcorrection to the motors via the motor controller. It contains the algorithm to fuse the sensor data. 

<code>python recv.py</code>