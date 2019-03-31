# Auto Drive

This hosts the code fot the second phase of Science Fair project (2019 PRSEF, 2019 PJAS, and 2019 ISEF).<br>
The code for phase I (PRSEF 2018) is in the old_system directory.

tracking.final.py: This is the code to run on each infrastructure camera, which identifies the vehicle and computes steering adjustment. Adjustment is transmitted over UDP to the rpi vehicle.

<code>python tracking.final.py <camid> <interval/duration> <null> <outage hreshold> </code>

rpi/: Code for the Raspberry Pi

Visit my <a href="https://sanjayseshan.github.io/autodrive/">project website</a> for detailed information.