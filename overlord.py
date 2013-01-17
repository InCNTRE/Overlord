"""
Overlord

An Openflow control plane solution.
1. Group devices via layer2 rules
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from Overlord.Devices import Devices as oDev
from Overlord.Links import Links as oLnk
from Overlord.Hosts import Hosts as oHos
from Overlord.Forwarding import Forwarding as oFwd
from Overlord.Lib.Web import OverlordMessage as oMsg
from pymongo import Connection

import time
from threading import Thread

log = core.getLogger()
db = None
devices = None
links = None
hosts = None
forwarding = None

######################################################

def launch():
    # Define modules as global for assignment
    global db
    global devices
    global links
    global hosts
    global forwarding

    # POX Lib
    core.openflow.addListenerByName("ConnectionUp", _handleConnectionUp)
    core.openflow.addListenerByName("ConnectionDown", _handleConnectionDown)
    core.openflow.addListenerByName("PacketIn", _handlePacketIn)
    
    # Overlord Lib
    devices = oDev.Devices()
    hosts = oHos.Hosts()
    links = oLnk.Links()
    forwarding = oFwd.Forwarding()

    # Connect to db')
    conn = Connection()
    db = conn['overlord']

    # Initialize Message Queue')
    if "messages" in db.collection_names():
        db["messages"].drop()
        db.create_collection("messages", size=100000, max=100, capped=True)
        db.messages.insert({"message": "null"})
        
    # Overlord Events')
    oEvents = oMsg.OverlordMessage()
    oEvents.addListenerByName("WebCommand", _handleWebCommand)
    t = Thread(target=oEvents.run, args=(db,))
    t.setDaemon(True)
    t.start()

# This could probably be cleaned up a bit. Maybe push it down into forwarding.Group.
def _handleWebCommand(event):
    cmd = event.Command()
    try:
        if cmd[u"message"] == u"group":
            log.info("Got a Group Command")            
            try:
                host = hosts.GetInfo(log, db, cmd[u"mac"])
                host["group_no"] = str( cmd[u"group_no"] )
                db.hosts.save(host)

                flows = forwarding.Disconnect(host)
                switches = devices.AllConnections()
                for f in flows:
                    for k in switches:
                        switches[k].send(f)

                if host["group_no"] != "-1":
                    forwarding.Group(log, db, devices, links, host)
            except LookupError:
                log.error("Host does not exist or is unknown to the controller. Has the device ARP'd yet?")

        elif cmd[u"message"] == u"mirror":
            log.info("Got a Mirror Command")

        else:
            log.error("Got an Unknown Command")

    except KeyError:
        log.error("Recived invalid message")

def _handleConnectionUp(event):
    devices.Learn(log, db, event, fwding=forwarding, lnks=links)
    forwarding.Learn(event)

def _handleConnectionDown(event):
    devices.Forget(log, event)
    forwarding.Forget(event)

def _handlePacketIn(event):
    # Track Network Devices
    devices.Learn(log, db, event)
    # Learn Network Device Links
    links.Learn(log, event)
    # Track Hosts
    hosts.Learn(log, db, forwarding, links, event)
