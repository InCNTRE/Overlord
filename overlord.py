"""
Overlord - InCNTRE 2013
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from Overlord.Devices import Devices as oDev
from Overlord.Links import Links as oLnk
from Overlord.Hosts import Hosts as oHos
from Overlord.Forwarding import Forwarding as oFwd
from Overlord.Lib.Web import OverlordMessage as oMsg
from src.database import *

import time
from threading import Thread

log = core.getLogger()
links = None
hosts = None

######################################################

def launch():
    # Define modules as global for assignment
    global links
    global hosts

    # Connect to db
    tmp_db = Database()
    core.register("db", tmp_db)

    # Set all hosts to inactive
    for h in core.db.find_hosts({}):
        h['active'] = False
        core.db.update_host(h)
        
    # POX Lib
    core.openflow.addListenerByName("ConnectionUp", _handleConnectionUp)
    core.openflow.addListenerByName("ConnectionDown", _handleConnectionDown)
    core.openflow.addListenerByName("PacketIn", _handlePacketIn)
    core.openflow.addListenerByName("PortStatus", _handlePortStatus)

    # Overlord Lib
    core.devices = oDev.Devices()
    hosts = oHos.Hosts()
    links = oLnk.Links()
    
    core.forwarding = oFwd.Forwarding()
    core.forwarding.add_listener("new_flows", _handleNewFlows)
    hosts.add_listener("host_moved", _handleHostMoved)

    # Overlord Events')
    oEvents = oMsg.OverlordMessage()
    oEvents.addListenerByName("WebCommand", _handleWebCommand)
    t = Thread(target=oEvents.run)
    t.setDaemon(True)
    t.start()

def _handleHostMoved(event):
    host = event.host
    flows = core.forwarding.Disconnect(host)
    switches = core.devices.AllConnections()
    for f in flows:
        for k in switches:
            switches[k].send(f)
    if host["group_no"] != "-1":
        core.forwarding.Group(log, core.devices, links, host)

def _handleNewFlows(event):
    for dpid in event.flows:
        for f in event.flows[dpid]:
            core.devices.Connection(log, dpid).send(f)

# This could probably be cleaned up a bit. Maybe push it down into forwarding.Group.
def _handleWebCommand(event):
    cmd = event.Command()
    try:
        if cmd[u"message"] == u"group":
            print("Got a Group Command")            
            try:
                host = core.db.find_host({"mac":str(cmd[u"mac"])})
                host["group_no"] = str(cmd[u"group_no"])
                core.db.update_host(host)

                flows = core.forwarding.Disconnect(host)
                switches = core.devices.AllConnections()
                for f in flows:
                    for k in switches:
                        switches[k].send(f)

                if host["group_no"] != "-1":
                    core.forwarding.Group(log, core.devices, links, host)
            except LookupError:
                log.error("Host does not exist or is unknown to the controller. Has the device ARP'd yet?")

        elif cmd[u"message"] == u"mirror":
            log.info("Got a Mirror Command")

        else:
            log.error("Got an Unknown Command")

    except KeyError:
        log.error("Recived invalid message")

def _handleConnectionUp(event):
    core.forwarding.Learn(event)
    core.devices.Learn(log, event, lnks=links)
    links.Learn(event)

def _handleConnectionDown(event):
    core.devices.Forget(log, event)
    core.forwarding.Forget(event)

def _handlePacketIn(event):
    # Learn Network Device Links
    l = links.Learn(event)
    if not l is None:
        core.forwarding.add_link(l[0], l[1], l[2])
    # Track Hosts
    hosts.learn(event)

def _handlePortStatus(event):
    core.devices.Learn(log, event)
