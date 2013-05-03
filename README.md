# Overlord
Overlord is a control plane network device database built to facilitate rapid OpenFlow network configuration. By using each host’s source mac address as an unique identifier, Overlord is able to detect changes in host IP addresses, source port numbers, and top-of-rack DPIDs. Overlord also provides basic layer2 packet forwarding, and network group creation.
Important: Overlord only uses ARP to update its internal database.

## Installation

### Install Dependencies
1. mongodb-10gen
2. pymongo
3. POX
4. nodejs

### Get Overlord
Clone or Fork Overlord into `~/POX_SOURCE/pox`
```
cd ~/POX_SOURCE/pox/
git clone https://github.com/jonstout/overlord.git
```

### Start Overlord
Start the OverlordWeb web server.
```
cd ~/POX_SOURCE/pox/Overlord/frontend
node app.js &
```

Start the Overlord controller
```
cd ~/pox/
./pox.py Overlord.overlord
```

## OpenFlow Hardware Requirements
1. Match on source mac
2. Match on destination mac
4. Match on Ethertype
