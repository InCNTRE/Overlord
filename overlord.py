# Overlord 2012

from pox.core import core
import pox.openflow.libopenflow_01 as of
from Overlord.Devices import Devices as oDev
from Overlord.Links import Links as oLnk
from Overlord.Hosts import Hosts as oHos
from Overlord.Forwarding import Forwarding as oFwd
from pymongo import Connection

log = core.getLogger()
db = None

devices = None
links = None
hosts = None
forwarding = None

def launch():
    # POX Lib
    core.openflow.addListenerByName("ConnectionUp", _handleConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handlePacketIn)

    # Overlord Lib
    global devices
    devices = oDev.Devices()
    global hosts
    hosts = oHos.Hosts()
    global links
    links = oLnk.Links()
    global forwarding
    forwarding = oFwd.Forwarding()

    # Connect to db
    global db
    conn = Connection()
    db = conn['overlord']

def _handleConnectionUp(event):
    devices.Learn(log, event)

def _handlePacketIn(event):
    # Track Network Devices
    devices.Learn(log, event)
    # Learn Network Device Links
    links.Learn(log, event)
    # Track Hosts
    hosts.Learn(log, db, forwarding, links, event)
