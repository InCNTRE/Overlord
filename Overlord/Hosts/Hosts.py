# import Overlord.Hosts
import inspect
class Hosts(object):
    """Learn and track Host Devices"""
    def __init__(self):
        self.known_hosts = []

    def Learn(self, log, event):
        """Learn port, mac, and ip"""
        pkt = event.parse()

        # ARP Packet
        if pkt.type == 2054:
            arp_pkt = pkt.next
            self.memorizeHost(event.dpid, arp_pkt.hwsrc, arp_pkt.protosrc, event.port)
            log.debug(str(event.dpid)+' '+str(arp_pkt.hwsrc)+' '+str(arp_pkt.protosrc)+' '+str(event.port))


    def memorizeHost(self, dpid, mac, ip, port):
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
