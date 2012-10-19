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
    hosts.Learn(log, db, event)

    # packet = event.parsed
    # overlord.learn(packet)

    # if (packet.dst in overlord.known_hosts):
    #     if (overlord.grouped(packet.src, packet.dst)):
    #         overlord.connect(overlord.path_strategy, packet.src, packet.dst)
    #         return True
    # # Install drop action on packet.src or paket.dst
    # msg = of.ofp_flow_mod()
    # msg.match.dl_src = packet.src
    # msg.match.dl_dst = packet.dst
    # event.connection.send(msg)
    # # ARP for unknown packet dst
    # msg = of.arp()
    # msg.dl_src = packet.src
    # msg.dl_dst = 0
    # msg.nw_src = packet.src_ip
    # msg.nw_dst = packet.dst_ip
    # ofp_msg = of.packet_out(msg)
    # event.connection.send(ofp_msg)
    # return False
