# Overlord
Overlord is an automated network device database built to address rapidly changing network configurations and labs with limited network resources. Overlord, built on the POX Openflow Controller platform, manages connections between end hosts by placing them in defined L2 network groups. Packets switched between groups are identified by source and destination mac. Overlord also acts as an automated network device database. By using each host’s source mac address as an unique identifier, Overlord is able to detect changes in host IP addresses, source port numbers, and top-of-rack DPIDs. Overlord tracks devices by intercepting ARP messages and updating device ARP tables.
Important: Overlord only uses ARP to update its internal database.

## Installation

### Install Dependencies
1. mongodb-10gen
2. pymongo
3. POX
4. OverlordWeb

### Get Overlord
Clone or Fork Overlord into `~/pox/pox`
```
cd ~/pox/pox/
git clone https://github.com/jonstout/overlord.git
```

### Start Overlord
Start the Overlord controller

```
cd ~/pox/
./pox.py Overlord.overlord
```

Start the OverlordWeb web server.

```
cd ~/OverlordWeb
node index.js
```

## OpenFlow Hardware Requirements
1. Match on source mac
2. Match on destination mac
4. Match on Ethertype
