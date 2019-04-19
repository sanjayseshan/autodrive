---
layout: default
---

# Intel ISEF Final Abstract

Studies predict that demand for autonomous vehicles will increase tenfold between 2019 and 2026.
However, recent high-profile accidents have significantly impacted consumer confidence in this
technology. The cause for many of these accidents can be traced back to the inability of these
vehicles to correctly sense the impending danger. In response, manufacturers have been
improving the already extensive on-vehicle sensor packages to ensure that the system always has
access to the data necessary to ensure safe navigation. However, these sensor packages only
provide a view from the vehicle’s perspective and, as a result, autonomous vehicles still require
frequent human intervention to ensure safety.

To address this issue, I developed a system, called Horus, that combines on-vehicle and
infrastructure- based sensors to provide a more complete view of the environment, including areas
not visible from the vehicle. I built a small-scale experimental testbed as a proof of concept. My
measurements of the impact of sensor failures showed that even short outages (~1 second) at
slow speeds (~25 km/hr scaled velocity) prevents vehicles that rely on on-vehicle sensors from
navigating properly. My experiments also showed that Horus dramatically improves driving safety
and that the sensor fusion algorithm selected plays a significant role in the quality of the navigation.
With just a pair of infrastructure sensors, Horus could tolerate sensors that fail 40% of the time and
still navigate safely. These results are a promising first step towards safer autonomous vehicles.

# Motivation

Market research predicts that the demand for autonomous vehicles will increase tenfold between 2019 and 2026. However, recent high-profile incidents, such as the fatal accidents with Uber and Tesla self-driving vehicles, have significantly impacted consumer confidence in this technology. A recent study by AAA reports that three-quarters of Americans are too afraid to ride in an autonomous vehicle and two-thirds feel less safe when self-driving cars are present. In order for autonomous cars to reach their potential, they must be made safer and more reliable.

Many of the past autonomous vehicle failures can be traced to failures in making accurate sensor observations. Existing approaches to improving autonomous driving focus on improving the already extensive on-vehicle sensor packages to ensure that the system always has access to the data necessary to ensure safe navigation. However, these sensors will always be limited by the view available from the autonomous vehicle. Sensors that already exist in the surrounding infrastructure, such as cameras mounted on roads and bridges, could provide autonomous vehicles with a much more complete view of their surroundings and enable much safer autonomous driving. My project explores the challenges associated with effectively combining the sensor observations made by on-vehicle and infrastructure sensors to improve autonomous driving performance and safety. 

# Brief Overview of Project

Currently, autonomous vehicle manufacturers focus only on adding on-vehicle sensors, providing a limited view from the car’s perspective, which often requires human intervention. My project looks at improving the performance and safety of autonomous vehicles by incorporating sensors that already exist in our infrastructure, such as CCTV cameras on bridges and buildings, along side the on-vehicle sensors. Through my experiments in a custom test-bed, I discovered that using external sensors significantly improves the performance of autonomous vehicles, but it is important which mathematical algorithm is used to fuse the data from multiple sensors.

# Awards

Phase II:
*  Intel ISEF nomination
*  3rd Place in Engineering/Robotics at Pittsburgh Regional Science and Engineering Fair
*  FedEx Sponsor award at Pittsburgh Regional Science and Engineering Fair
*  1st Place Engineering at Pensylvania Junior Academy of Science Region 7
*  Carnegie Mellon University Chi Epsilon Sponsor Award Junior Academy of Science Region 7

Phase I:
* 2nd Place in Engineering/Robotics at Pittsburgh Regional Science and Engineering Fair
* Fedex Ground Sponsor Award
* Harrisburg University of Science & Technology Sponsor Award
* Innovation Works Sponsor Award

# Future Plans

Phase III of the project will look at: 1) controlling multiple vehicles concurrently; 2) more realistic testing using simulation software and actual car tests with wireless OBD-II interface; and 3) vehicle identification without color codes (using feature identification algorithms, such as SIFT)
