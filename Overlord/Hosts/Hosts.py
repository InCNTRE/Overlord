# import Overlord.Hosts
from pox.core import core
import pox.openflow.libopenflow_01 as of
import inspect

class Hosts(object):
    """Learn and track Host Devices"""
    def __init__(self):
        self.known_hosts = []

    def Learn(self, log, db, event):
        """Learn port, mac, and ip"""
        pkt = event.parse()

        # Learn device locations via ARP Packet
        if pkt.type == 2054:
            log.debug("Learning ARP")
            self.learnArp(log, db, event, pkt)

    def getHostGroup(self, hwaddr):
        return None

    def setHostGroup(self, hwaddr, group_no):
        pass

    def getGroupMembers(self, hwaddr, group_no):
        return []

    def knownHost(self, hwaddr):
        """
        Binary search (actually not sure about
        that) on self.known_hosts"""
        try:
            ## Get hwaddr that's mapped to ipaddr
            self.known_hosts.index(hwaddr)
            return True
        except ValueError:
            return False

    def memorizeHost(self, log, db, dpid, port, ip, mac):
        """
        It makes more since to use something like a
        binary tree here since count(known_hosts)
        could be quite large.
        The dpid, port, ip, and mac should be
        published to db here.
        Using insertion sort here for simplicity. No
        need to over optimize atm.
        [(mac, {'dpid':x, 'ip':x, 'port':x})]"""
        i = 0
        while i < len(self.known_hosts) and mac >= self.known_hosts[i]:
            i += 1
        # Makes sure macs aren't duplicated, only updated
        if i == 0 or mac != self.known_hosts[i-1]:
            log.debug('Memorizing ' + str(self.known_hosts))
            self.known_hosts.insert(i, mac)
        
        # Save the dpid, ip, and port to the database here
        host = db.hosts.find_one({"mac": mac})
        if host == None:
            db.hosts.save({"parent": str(dpid), "port_no": port, "ip": ip, "mac": mac})
        else:
            host["parent"] = str(dpid)
            host["port_no"] = str(port)
            host["ip"] = str(ip)
            host["mac"] = str(mac)

    def learnArp(self, log, db, event, pkt):
        # Learn the host information
        arp_pkt = pkt.next

        # Find out what group the device is in. If he's even in one.
        group_no = self.getHostGroup(arp_pkt.hwsrc)
        self.memorizeHost(log, db, event.dpid, event.port, arp_pkt.protosrc, arp_pkt.hwsrc)
        log.debug(str(event.dpid)+' '+str(event.port)+' '+str(arp_pkt.protosrc)+' '+str(arp_pkt.hwsrc))

        if group_no == "-1":
            # Drop everything from this source for 3 seconds (group changes may occour)
            msg = of.ofp_flow_mod(hard_timeout=3)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.protodst = arp_pkt.protodst
            event.connection.send(msg)
        elif group_no != None:
            # Forward to group members that are known
            # if protodst is known and group_nos are equal:
            #     send arp reply
            #     and build connection
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
