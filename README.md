# Network Latency Fingerprinting


A physics oriented cybersecurity project that uses round trip time (RTT) and signal propagation constraints in order to detect anomalous or spoofed traffic.


## Overview


The project demonstrates the physical limits on signal speed could be used as a security signal in analyzing network traffic. By Measuring RTT then modeling the baseline behavior, the system detects anomalous or potentially spoofed paths.


The intention of the project is to focus more on practical SOC style detection rather than machine learning.


## Key Idea


Network traffic is ultimately constrained by physics: signals are unable to travel faster than the speed of light through fiber. If the observed latency deviates significantly from the stables baseline, it could potentially indicate:


   - Routing changes
   - Proxy/VPN insertion
   - MITM relays
   - Congestion DOS artifacts


This project uses latency fingerprinting to surface these anomalies.


## How It Works


1. Measure RTT using TCP connection timing
2. Build a baseline based upon initial samples
3. Compute the mean and standard deviations
4. Flag outliers using configurable threshold
5. Log the results to the CSC
6. Generate a visualization highlighting found anomalies



