# Overlord 2012

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
    global link
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

    # Connect to db
    conn = Connection()
    db = conn['overlord']
    
    # Overlord Events
    oEvents = oMsg.OverlordMessage()
    oEvents.addListenerByName("WebCommand", _handleWebCommand)
    t = Thread(target=oEvents.run, args=(db,))
    t.setDaemon(True)
    t.start()

def _handleWebCommand(event):
    cmd = event.Command()
    
    try:
        if cmd[u"message"] == u"group":
            log.debug("Got a Group Command")
            mac = cmd["mac"]
            group_no = cmd["group_no"]
            
            try:
                # Pull the DB info and update. Then push down rules.
                host = hosts.GetInfo(log, db, mac)
                host["group_no"] = str(group_no)
                db.hosts.save(host)
                # Disconnect host from previous devices. Then regroup.
                forwarding.Disconnect(log, devices, host)
                #forwarding.Group(log, db, links, host, group_no)
            except LookupError:
                log.error("Host does not exist or is unknown to the controller. Has the device ARP'd yet?")

        elif cmd[u"message"] == u"mirror":
            log.debug("Got a Mirror Command")
        else:
            log.debug("Got an Unknown Command")
    except KeyError:
        log.error("Recived invalid message")

def _handleConnectionUp(event):
    devices.Learn(log, event)

def _handleConnectionDown(event):
    devices.Forget(log, event)

def _handlePacketIn(event):
    # Track Network Devices
    devices.Learn(log, event)
    # Learn Network Device Links
    links.Learn(log, event)
    # Track Hosts
    hosts.Learn(log, db, forwarding, links, event)
