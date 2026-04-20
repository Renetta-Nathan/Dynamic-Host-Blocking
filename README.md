# Dynamic Host Blocking System using SDN

## Project Overview

This project implements a Dynamic Host Blocking System using Software Defined Networking (SDN).
It uses a Ryu controller and Mininet to monitor network traffic and dynamically block suspicious hosts based on behavior.

---

## Objective

* Detect abnormal traffic patterns (for example, flooding)
* Dynamically block malicious hosts
* Demonstrate controller-switch interaction using OpenFlow
* Analyze network behavior before and after blocking

---

## System Architecture

### Network Topology

```
   h1 --------\
               \
                s1 -------- Controller (Ryu)
               /
   h2 --------/
              
   h3 --------/
```

* h1, h2, h3 are hosts
* s1 is the OpenFlow switch
* Controller manages flow rules

---

### Workflow Diagram

```
+---------+        packet_in         +--------------+
| Switch  | -----------------------> | Controller   |
|  (s1)   |                          |   (Ryu)      |
+---------+                          +--------------+
     |                                      |
     |                           Analyze traffic
     |                                      |
     |                           Is it suspicious?
     |                          /             \
     |                        Yes             No
     |                         |               |
     |                 Install DROP       Forward normally
     |                     rule                |
     |                         \              /
     |                          \            /
     +---------------------------\----------+
                                  v
                             Apply flow rule
```

---

## Key Features

* Learning switch implementation
* Packet monitoring and counting
* Dynamic threshold-based blocking
* Automatic installation of DROP flow rules
* Temporary blocking using idle timeout

---

## Technologies Used

* Python
* Ryu SDN Controller
* Mininet
* OpenFlow Protocol

---

## Setup Instructions

### 1. Install dependencies

```
sudo apt update
sudo apt install python3-pip python3-venv mininet
pip install ryu
```

---

### 2. Run the controller

```
ryu-manager dynamic_block.py
```

---

### 3. Start Mininet

```
sudo mn --topo single,3 --controller remote
```

---

## Testing Scenarios

### Scenario 1: Normal Traffic (Allowed)

```
mininet> h1 ping h2
```

Expected result:

* Communication succeeds

---

### Scenario 2: Suspicious Traffic (Blocked)

```
mininet> h1 ping -f h2
```

Expected result:

* Flooding detected
* Host is blocked automatically

---

## Verification

### Check flow rules

```
sudo ovs-ofctl dump-flows s1
```

Expected:

* Normal forwarding rules
* High priority DROP rule for blocked host

---

## Output / Proof

* Normal Ping (Before Blocking)
  <img width="907" height="337" alt="image" src="https://github.com/user-attachments/assets/01d9a4f7-03c7-446e-a9ca-01364ca79d31" />
  
* Flood Ping (Attack Simulation)
  
  <img width="1089" height="379" alt="image" src="https://github.com/user-attachments/assets/9fc532c3-c16b-45ce-9416-3242e66da347" />

* After Blocking Happens
  
  <img width="1141" height="354" alt="image" src="https://github.com/user-attachments/assets/e292da03-8ed1-47b6-9b3a-ed0ee3e46dff" />

* Controller logs showing blocking
  
  <img width="406" height="529" alt="image" src="https://github.com/user-attachments/assets/65fd93bd-3ae7-41e4-b359-cb770dbe88fa" />

---

## How It Works

1. Switch sends packets to controller (packet_in)
2. Controller counts packets per host
3. If threshold exceeded, host is marked suspicious
4. Controller installs a DROP rule
5. Traffic from that host is blocked

---

## Author

Renetta Nathan

---

## Conclusion

This project demonstrates how SDN enables dynamic and programmable network security by allowing the controller to monitor and control traffic behavior in real time.
