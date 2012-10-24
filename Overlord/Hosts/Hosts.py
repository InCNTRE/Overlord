# import Overlord.Hosts
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.arp import arp

class Hosts(object):
    """Learn and track Host Devices"""
    def __init__(self):
        self.known_hosts = []

    def Learn(self, log, db, forwarding, links, event):
        """Learn port, mac, and ip"""
        pkt = event.parse()

        # Learn device locations via ARP Packet
        if pkt.type == 2054:
            log.debug("Learning ARP")
            self.learnArp(log, db, forwarding, links, event, pkt)

    def getHostGroup(self, log, db, mac):
        host = db.hosts.find_one({"mac": str(mac)})
        if host != None:
            return host["group_no"]
        else:
            return None

    def setHostGroup(self, log, db, mac, group_no):
        host = db.hosts.find_one({"mac": str(mac)})
        host["group_no"] = group_no
        db.hosts.save(host)
        log.debug('Moved ' + str(mac) + ' into group ' + str(group_no))

    def getGroupMembers(self, log, db, mac, group_no):
        members = db.hosts.find({"mac": {"$ne": str(mac)}, "group_no": group_no})
        if members: return members; return {}

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

        for h in self.known_hosts:
            if h == str(mac):
                host = db.hosts.find_one({"mac": str(mac)})
                host["_parent"] = str(dpid)
                host["port_no"] = str(port)
                host["ip"] = str(ip)
                host["mac"] = str(mac)
                db.hosts.save(host)
                return host
        
        self.known_hosts.append(str(mac))
        data = {"_parent": str(dpid), "port_no": str(port), "ip": str(ip), "mac": str(mac), "group_no": "-1", "group_was": "-1"}
        db.hosts.save(data)
        return data
        """
        i = 0
        while i < len(self.known_hosts) and mac >= self.known_hosts[i]:
            i += 1
        # Makes sure macs aren't duplicated, only updated
        if i == 0 or mac != self.known_hosts[i-1]:
            log.debug('Memorizing ' + str(self.known_hosts))
            self.known_hosts.insert(i, mac)
            log.debug('Discovered Host: '+str(mac)+' '+str(ip))
        
        # Save the dpid, ip, and port to the database here incase something changed
        host = db.hosts.find_one({"mac": str(mac)})
        if host == None:
            data = {"_parent": str(dpid), "port_no": str(port), "ip": str(ip), "mac": str(mac)}#, "group_no": "-1"})
            db.hosts.save(data)
            return data
        else:
            host["_parent"] = str(dpid)
            host["port_no"] = str(port)
            host["ip"] = str(ip)
            host["mac"] = str(mac)
            db.hosts.save(host)
            return host"""

    def learnArp(self, log, db, forwarding, links, event, pkt):
        # Learn the host information
        arp_pkt = pkt.next
        host1 = self.memorizeHost(log, db, event.dpid, event.port, arp_pkt.protosrc, arp_pkt.hwsrc)
        
        # Find out what group the device is in. If he's even in one.
        group_no = host1["group_no"]#self.getHostGroup(log, db, arp_pkt.hwsrc)
        if group_no == "-1":
            # Drop everything from this source for 3 seconds (group changes may occour)
            msg = of.ofp_flow_mod(hard_timeout=3)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.dl_type = 0x0806
            msg.match.protodst = arp_pkt.protodst
            event.connection.send(msg)
        elif group_no != None:
            # Forward to group members that are known
            # if protodst is known and group_nos are equal:
            #     send arp reply
            #     and build connection
            #host1 = db.hosts.find_one({"mac": str(arp_pkt.hwsrc)})
            host2 = db.hosts.find_one({"ip": str(arp_pkt.protodst)})

            log.debug(str(host1))
            log.debug(str(host2))

            if host2 != None:
                # Something changed so remove all previous flow regarding this device
                forwarding.Disconnect(log, event, host1)
                # Rebuild the links between the device and group members
                for h in self.getGroupMembers(log, db, arp_pkt.hwsrc, group_no):
                    log.debug(str(host1) + str(host2))
                    forwarding.Connect(log, links, event, host1, h)
                    #     send arp reply
                    amsg = arp()
                    amsg.opcode = 2
                    amsg.hwsrc = EthAddr(h["mac"])
                    amsg.hwdst = EthAddr(host1["mac"])
                    amsg.protosrc = IPAddr(str(h["ip"]))
                    amsg.prododst = IPAddr(str(host1["ip"]))
                    pkt.next = amsg
                    pkt_out= of.ofp_packet_out()
                    pkt_out.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
                    pkt_out.data = pkt
                    event.connection.send(pkt_out)
            else:
                # Drop everything from this source
                msg = of.ofp_flow_mod(hard_timeout=3)
                msg.match.dl_src = arp_pkt.hwsrc
                msg.match.protodst = arp_pkt.protodst
                event.connection.send(msg)
        else:
            # Update group_no to group -1
            self.setHostGroup(log, db, arp_pkt.hwsrc, "-1")
            # Drop everything from this source
            msg = of.ofp_flow_mod(hard_timeout=3)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.protodst = arp_pkt.protodst
            event.connection.send(msg)
