# Overlord 2012

from pox.core import core
import pox.openflow.libopenflow_01 as of
from Overlord.Devices import Devices as oDev
from Overlord.Links import Links as oLnk
from Overlord.Hosts import Hosts as oHos
from Overlord.Forwarding import Forwarding as oFwd
from pymongo import Connection

from pox.lib.recoco.recoco import *
from pox.lib.revent.revent import EventMixin, Event
import time

log = core.getLogger()
db = None

devices = None
links = None
hosts = None
forwarding = None

class WebCommand(Event):
    def __init__(self, command):
        Event.__init__(self)
        self.command = command
        
    def Command(self):
        return self.command

class OverlordMessage(EventMixin):
    _eventMixin_events = set([WebCommand])
    
    def __init__(self):
        EventMixin.__init__(self)

    def run(self, db):
        latest = db.messages.find({}, await_data=True, tailable=True).sort("$natural", 1).limit(1)
        
        try:
            last = None
            while True:
                try:
                    cmd = latest.next()
                    last = cmd["_id"]
                    # Raise Event
                    self.raiseEventNoErrors(WebCommand(cmd))
                except StopIteration:
                    time.sleep(3)
                finally:
                    latest = db.messages.find({"_id": {"$gt": last}}).limit(1)
        except KeyboardInterrupt:
            print "ctrl-c was pressed"

######################################################

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
    
    # Overlord Events
    oEvents = OverlordMessage()
    oEvents.addListenerByName("WebCommand", _handleWebCommand)
    core.callLater(oEvents.run, db)

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
