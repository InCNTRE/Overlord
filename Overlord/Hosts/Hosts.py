# import Overlord.Hosts
from pox.core import core
import pox.openflow.libopenflow_01 as of
import inspect

class Hosts(object):
    """Learn and track Host Devices"""
    def __init__(self):
        self.known_hosts = []

    def Learn(self, log, event):
        """Learn port, mac, and ip"""
        pkt = event.parse()

        # Learn device locations via ARP Packet
        if pkt.type == 2054:
            log.debug("Learning ARP")
            self.learnArp(log, event, pkt)

    def getHostGroup(self, hwaddr):
        return None

    def setHostGroup(self, hwaddr, group_no):
        pass

    def getGroupMembers(self, hwaddr, group_no):
        return []

    def knownHost(self, hwaddr):
        """binary search self.known_hosts"""
        return True

    def memorizeHost(self, dpid, port, ip, mac):
        """Yeah insertion sort sucks here, but fuck it.
        Save the Host info to databse by mac. Save only
        mac locally.
        [(000000, {'dpid':x, 'ip':x, 'port':x})]"""
        i = 0
        while i < len(self.known_hosts) and mac > self.known_hosts[i]:
            i += 1
        self.known_hosts.insert(i, mac)
        # UPDATE HERE
        # Save the dpid, ip, and port to the database here

    def learnArp(self, log, event, pkt):
        # Learn the host information
        arp_pkt = pkt.next

        # Find out what group the device is in. If he's even in one.
        group_no = self.getHostGroup(arp_pkt.hwsrc)
        self.memorizeHost(event.dpid, event.port, arp_pkt.protosrc, arp_pkt.hwsrc)
        log.debug(str(event.dpid)+' '+str(event.port)+' '+str(arp_pkt.protosrc)+' '+str(arp_pkt.hwsrc))

        if group_no == "-1":
            # Drop everything from this source for 3 seconds (group changes may occour)
            msg = of.ofp_flow_mod(hard_timeout=3)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.protodst = arp_pkt.protodst
            event.connection.send(msg)
        elif group_no != None:
            # Forward to group members that are known
            for member in self.getGroupMembers(arp_pkt.hwsrc, group_no):
                forwarding.Connect(arp_pkt.hwsrc, member)
        else:
            # Update group_no to group -1
            self.setHostGroup(arp_pkt.hwsrc, "-1")
            # Drop everything from this source
            msg = of.ofp_flow_mod(hard_timeout=3)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.protodst = arp_pkt.protodst
            event.connection.send(msg)
