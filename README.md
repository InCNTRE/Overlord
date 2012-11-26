# Overlord
Overlord is an Openflow network application built on the POX framework. Overlord was built to manage rapidly changing networks by tracking host IP addresses, source port numbers, and top-of-rack DPIDs.

## Installation

### Install Dependencies
1. mongodb-10gen
2. pymongo
3. POX
4. OverlordWeb

### Get Overlord
Clone or Fork Overlord into /pox/pox
```
cd ~/pox/pox/
git clone https://github.com/jonstout/overlord.git
```

### Start Overlord
Start the Overlord controller

```
cd ~/pox/
./pox.py overlord.overlord
```

Start the OverlordWeb web server.

```
cd ~/OverlordWeb
node index.js
```

## OpenFlow Hardware Requirements
1. Match on source mac
2. Match on destination mac
3. Match on destination ip
4. Match on Ethertype
