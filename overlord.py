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
    # POX Lib
    core.openflow.addListenerByName("ConnectionUp", _handleConnectionUp)
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

    if u"message" in cmd.keys():
        if cmd[u"message"] == u"group":
            log.debug("Got a Group Command")
            mac = cmd["mac"]
            group_no = cmd["group_no"]

            host = hosts.GetInfo(log, db, mac)
            forwarding.Dis(log, host)
            #forwarding.Group(log, host, group_no)
        elif cmd[u"message"] == u"mirror":
            log.debug("Got a Mirror Command")
        else:
            log.debug("Got an Unknown Command")
    else:
        log.error("Recived invalid message")

def _handleConnectionUp(event):
    devices.Learn(log, event)

def _handlePacketIn(event):
    # Track Network Devices
    devices.Learn(log, event)
    # Learn Network Device Links
    links.Learn(log, event)
    # Track Hosts
    hosts.Learn(log, db, forwarding, links, event)
