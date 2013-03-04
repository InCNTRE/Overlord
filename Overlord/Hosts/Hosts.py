# import Overlord.Hosts
from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.arp import arp
from ..Lib.Events import Event, Eventful

import pox.openflow.libopenflow_01 as of

class Hosts(Eventful):
    """Learn and track Host Devices"""
    def __init__(self):
        Eventful.__init__(self)
        self.known_hosts = {}
        # For when a device has been moved.
        self.add_event("host_moved")

    def Learn(self, log, db, forwarding, links, devices, event):
        """Learn port, mac, and ip"""
        pkt = event.parse()

        # Learn device information via ARP Packet
        if pkt.type == 2054:
            self.learnArp(log, db, forwarding, links, devices, event, pkt)

    def GetInfo(self, log, db, mac):
        host = db.hosts.find_one({"mac": str(mac)})
        if host == None:
            raise LookupError("Host does not exist")
        return host

    def getGroupMembers(self, log, db, mac, group_no):
        members = db.hosts.find({"mac": {"$ne": str(mac)}, "group_no": group_no})
        if members: return members; return {}

    # Returns a tuple (db_data, last_local_known_group)
    def memorizeHost(self, log, db, dpid, port, ip, mac):
        """
        Checks if host has been seen before. If not save a basic
        config locally. If the device has already been found
        ensure dpid and port_no have not changed. If either dpid
        or port_no have changed handle_event("host_moved").
        """
        host = db.hosts.find_one({"mac": str(mac)})

        if host == None:
            # If the source mac is not known add a local (mac, group) entry,
            #  and push the known information to the database.
            host = {"_parent": str(dpid), "port_no": str(port), "ip": str(ip), "mac": str(mac), "group_no": "-1", "active": True}
        else:
            host["_parent"] = str(dpid)
            host["port_no"] = str(port)
            host["ip"] = str(ip)
            host["mac"] = str(mac)
            host["active"] = True
            log.info("Got ARP from: {}".format(mac))

            if str(mac) in self.known_hosts:
                try:
                    if str(dpid) != self.known_hosts[str(mac)]["_parent"] or \
                            str(port) != self.known_hosts[str(mac)]["port_no"]:
                        e = Event()
                        e.host = host
                        self.handle_event("host_moved", e)
                except:
                    log.info("Exception in lookup")
            else:
                log.info("Device {} not local".format(mac))
        
        db.hosts.save(host)
        self.known_hosts[str(mac)] = host
        return host

    def learnArp(self, log, db, forwarding, links, devices, event, pkt):
        """
        Learn or Update host information when an ARP packet is recieved
        for a device. Forward ARP messages to devices only if they are
        in the same group.
        """

        # Learn or Update the host information
        arp_pkt = pkt.next
        host2 = db.hosts.find_one({"ip": str(arp_pkt.protodst)})
        if host2 == None: return
        self.known_hosts[str(host2["mac"])] = host2
        host1 = self.memorizeHost(log, db, event.dpid, event.port, arp_pkt.protosrc, arp_pkt.hwsrc)
        if str(host1["group_no"]) != str(host2["group_no"]): return
        if str(host1["group_no"]) == "-1":
            # Drop all IP traffic from this host
            msg = of.ofp_flow_mod(hard_timeout=5)
            msg.match.dl_src = arp_pkt.hwsrc
            msg.match.dl_type = 0x0800
            event.connection.send(msg)
        else:
            # The ARP'n device src and dst exist and are in the same group
            # Send ARP Reply for dst device
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
            devices.Connection(log, host1["_parent"]).send(pkt_out)
            
