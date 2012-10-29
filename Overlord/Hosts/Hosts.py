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

    def GetInfo(self, log, db, mac):
        host = db.hosts.find_one({"mac": str(mac)})
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

        if host == None:
            # If the source mac is not known add a local (mac, group) entry,
            #  and push the known information to the database.
            self.known_hosts.append( (str(mac), "-1") )
            data = {"_parent": str(dpid), "port_no": str(port), "ip": str(ip), "mac": str(mac), "group_no": "-1"}
            db.hosts.save(data)
            self.known_hosts.append(str(mac), "-a")
            return (data, "-1")
        else:
            for h in self.known_hosts:
                if h[0] == str(mac):
                    host["_parent"] = str(dpid)
                    host["port_no"] = str(port)
                    host["ip"] = str(ip)
                    host["mac"] = str(mac)
                    db.hosts.save(host)
                    return (host, str(h[1]))

        # The host is known but not recorded locally. Save and Return.
        self.known_hosts.append((str(host["mac"]), str(host["group_no"])))
        return (host, str(host["group_no"]))


    def learnArp(self, log, db, forwarding, links, event, pkt):
        # Learn or Update the host information
        arp_pkt = pkt.next
        host1, last_group = self.memorizeHost(log, db, event.dpid, event.port, arp_pkt.protosrc, arp_pkt.hwsrc)
        
        # If the group_no in the database doesn't match what we know Disconnect
        #  this host from all others.
        print(str(host1["group_no"]) + " " + last_group)
        if str(host1["group_no"]) != str(last_group):
            forwarding.Disconnect(log, event, host1)
            self.setHostGroupLocal(log, str(host1["mac"]), str(host1["group_no"]))

        if str(host1["group_no"]) == "-1":
            # Drop all IP traffic from this host
            msg = of.ofp_flow_mod(idle_timeout=300)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.dl_type = 0x0800
            event.connection.send(msg)
        else:
            host2 = db.hosts.find_one({"ip": str(arp_pkt.protodst)})
            if host2 == None: return

            log.debug(str(host1))
            log.debug(str(host2))

            # ARPing a device that is known to exist and has the same group permissions
            if str(host1["group_no"]) == str(host2["group_no"]):
                # Rebuild the links between the device and group members
                #for h in self.getGroupMembers(log, db, arp_pkt.hwsrc, group_no):
                #    log.debug(str(host1) + str(h))
                forwarding.Connect(log, links, event, host1, host2)
                #self.setHostGroupLocal(host1["mac"], host1["group_no"])
                    #     send arp reply
                amsg = arp()
                amsg.opcode = 2
                amsg.hwsrc = EthAddr(host2["mac"])
                amsg.hwdst = EthAddr(host1["mac"])
                amsg.protosrc = IPAddr(str(host2["ip"]))
                amsg.prododst = IPAddr(str(host1["ip"]))
                pkt.next = amsg
                pkt_out= of.ofp_packet_out()
                pkt_out.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
                pkt_out.data = pkt
                event.connection.send(pkt_out)
