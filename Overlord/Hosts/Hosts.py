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

        # Learn device information via ARP Packet
        if pkt.type == 2054:
            self.learnArp(log, db, forwarding, links, event, pkt)

    def GetInfo(self, log, db, mac):
        host = db.hosts.find_one({"mac": str(mac)})
        if host == None:
            raise LookupError("Host does not exist")
        return host

    def getHostGroup(self, log, db, mac):
        host = db.hosts.find_one({"mac": str(mac)})
        if host != None:
            return host["group_no"]
        else:
            return None

    def setHostGroupLocal(self, log, mac, group_no):
        for h in self.known_hosts:
            if h[0] == mac:
                del(h)
                self.known_hosts.append((mac, group_no))
                print(self.known_hosts)
                return

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

    # Returns a tuple (db_data, last_local_known_group)
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
        host = db.hosts.find_one({"mac": str(mac)})

        # New host
        if host == None:
            # If the source mac is not known add a local (mac, group) entry,
            #  and push the known information to the database.
            self.known_hosts.append( (str(mac), "-1") )    
            host = {"_parent": str(dpid), "port_no": str(port), "ip": str(ip), "mac": str(mac), "group_no": "-1", "active": True}
            db.hosts.save(host)
        else:
            host["_parent"] = str(dpid)
            host["port_no"] = str(port)
            host["ip"] = str(ip)
            host["mac"] = str(mac)
            host["active"] = True
            db.hosts.save(host)
            
        if host not in self.known_hosts:
            self.known_hosts.append(host["mac"])

        return host

    def learnArp(self, log, db, forwarding, links, event, pkt):
        """
        Learn or Update host information when an ARP packet is recieved
        for a device. Forward ARP messages to devices only if they are
        in the same group.
        """
        # Learn or Update the host information
        arp_pkt = pkt.next
        host1 = self.memorizeHost(log, db, event.dpid, event.port, arp_pkt.protosrc, arp_pkt.hwsrc)
        
        if str(host1["group_no"]) == "-1":
            # Drop all IP traffic from this host
            msg = of.ofp_flow_mod(idle_timeout=300)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.dl_type = 0x0800
            event.connection.send(msg)
        else:
            host2 = db.hosts.find_one({"ip": str(arp_pkt.protodst)})
            if host2 == None or str(host1["group_no"]) != str(host2["group_no"]): return

            """
            # The ARP'n device src and dst exist and are in the same group
            # Send ARP Reply for dst device
            #
            # ?FIXME?: Forward arp packet might be better here...
            If a device's info changes and we don't adjust for the change, things
            might get out of sync? I need to know more about ARP.
            """
            pkt.src = EthAddr(host2["mac"])
            pkt.dst = EthAddr(host1["mac"])
            amsg = arp()
            amsg.opcode = 2
            amsg.hwsrc = EthAddr(host2["mac"])
            amsg.hwdst = EthAddr(host1["mac"])
            amsg.protosrc = IPAddr(str(host2["ip"]))
            amsg.protodst = IPAddr(str(host1["ip"]))
            pkt.next = amsg
            pkt_out= of.ofp_packet_out()
            pkt_out.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
            pkt_out.data = pkt
            event.connection.send(pkt_out)
            
