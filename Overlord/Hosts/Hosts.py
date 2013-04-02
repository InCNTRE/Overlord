# import Overlord.Hosts
from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.arp import arp
from ..Lib.Events import Event, Eventful

import pox.openflow.libopenflow_01 as of

class Hosts(Eventful):
    def __init__(self):
        Eventful.__init__(self)
        self.hosts = {}
        self.add_event("host-update")

    def learn(self, devices, event):
        """
        Intercept and inspect ARP messages.
        """
        pkt = event.parse()
        if pkt.type != 2054: return
        arp = pkt.next

        host_a = core.db.find_host({"mac": str(arp.hwsrc)})
        print("Learning about Host %s via ARP" % str(arp.hwsrc))

        h = {"_parent": str(event.dpid),
             "port_no": str(event.port),
             "ip": str(arp.protosrc),
             "mac": str(arp.hwsrc),
             "group_no": "-1", "active": True}
        
        if host_a is None:
            print("Host %s is new. Recording and adding to null group" % str(arp.hwsrc))
            self.hosts[str(arp.hwsrc)] = h
            core.db.update_host(h)
            return

        if not str(arp.hwsrc) in self.hosts:
            print("Host %s is new to local db. Syncing with remote db." % str(arp.hwsrc))
            h["group_no"] = host_a["group_no"]
            self.hosts[str(arp.hwsrc)] = h
            core.db.update_host(h)
            e = Event()
            e.host = host_a
            self.handle_event("host-update", e)

        print("Checking known host %s for state changes." % str(arp.hwsrc))
        if host_a["group_no"] != h["group_no"] or host_a["ip"] != h["ip"] \
                or host_a["port_no"] != h["port_no"] or host_a["_parent"] != h["_parent"] \
                or host_a["active"] != h["active"]:
            print("Saving host %s changes to db and installing new flows." % str(arp.hwsrc))
            self.hosts[str(arp.hwsrc)] = h
            core.db.update_host(h)
            e = Event()
            e.host = host_a
            self.handle_event("host-update", e)
        
        if host_a.group is "-1":
            print("Not broadcasting ARP from Host %s" % str(arp.hwsrc))
            return
        else:
            host_b = core.db.find_host({"ip": str(arp.protodst)})
            if host_b is None or host_b.group is -1: return
            #self.send_arp(devices, host_a, host_b)
            self.send_arp(host_a, host_b)
            
        """
        if host_a is None or host_a.group is -1:
            h = {"_parent": event.dpid,
                 "port_no": event.port,
                 "ip": str(arp.protosrc),
                 "mac": str(arp.hwsrc),
                 "group_no": -1, "active": True}
            try:
                self.hosts[str(arp.hwsrc)].update(h)
            except KeyError:
                self.hosts[str(arp.hwsrc)] = h
            core.db.update_host(h)
            return
        else:
            if not host_a.dpid is event.dpid or not host_a.port is event.port:
                # Host migrated to new location
                e = Event()
                e.host = host_a
                self.handle_event("host-update", e)

            host_b = core.db.find_host({"ip": str(arp.protodst)})
            if host_b is None or host_b.group is -1: return
            self.send_arp(devices, host_a, host_b)"""

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
