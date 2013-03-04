# import Overlord.Hosts
from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.arp import arp
from ..Lib.Events import Event, Eventful
# from pox.core import database

import pox.openflow.libopenflow_01 as of

class Hosts(Eventful):
    def __init__(self):
        Eventful.__init__(self)
        self.hosts = {}
        self.add_event("host-update")

    def learn(self, event):
        pkt = event.parse()
        if pkt.type != 2054: return
        arp = pkt.next

        host_a = database.find_host("mac", arp.hwsrc)
        if host_a is None or host_a.group is -1:
            h = {"_parent": event.dpid,
                 "port_no": event.port,
                 "ip": str(arp.protosrc),
                 "mac": str(arp.hwsrc),
                 "group_no": -1, "active": True}
            self.hosts[str(arp.hwsrc)].update(h)
            database.update_host(h)
            return
        else:
            if not host_a.dpid is event.dpid or not host_a.port is event.port:
                # Host migrated to new location
                e = Event()
                e.host = host_a
                self.handle_event("host-update", e)

            host_b = database.find_host("ip", arp.protodst)
            if host_b is None or host_b.group is -1: return
            self.send_arp(host_a, host_b)

    def send_arp(self, host_a, host_b):
        # The ARP'n device src and dst exist and are in the same group
        # Send ARP Reply for dst device
        pkt.src = EthAddr(host_b.mac)
        pkt.dst = EthAddr(host_a.mac)
        amsg = arp()
        amsg.opcode = 2
        amsg.hwsrc = EthAddr(host_b.mac)
        amsg.hwdst = EthAddr(host_a.mac)
        amsg.protosrc = IPAddr(str(host_b.ip))
        amsg.protodst = IPAddr(str(host_a.ip))
        pkt.next = amsg
        pkt_out= of.ofp_packet_out()
        pkt_out.actions.append(of.ofp_action_output(port=int(host_a.port)))
        pkt_out.data = pkt
        devices.Connection(log, host_a.dpid).send(pkt_out)
