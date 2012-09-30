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
            # Learn about the new Device
            arp_pkt = pkt.next
            self.memorizeHost(event.dpid, arp_pkt.hwsrc, arp_pkt.protosrc, event.port)
            log.debug(str(event.dpid)+' '+str(arp_pkt.hwsrc)+' '+str(arp_pkt.protosrc)+' '+str(event.port))
            # What group is he in? Find from database
            group_no = self.getHostGroup(arp_pkt.hwsrc)
            if group_no == -2:
                # New device, add to default -1 drop group in db
                # Install Drop(hwsrc, hwdst)
                pass
            elif group_no == -1:
                # Already in defautl drop group
                # Install Drop(hwsrc, hwdst)
                pass
            else:
                if self.knownHost(arp_pkt.hwdst):
                    if group_no == self.getHostGroup(arp_pkt.hwdst):
                        # Add forwarding rules
                        pass
                    else:
                        # They're not defined to talk together
                        # Install Drop(hwsrc, hwdst)
                        # Install Drop(hwdst, hwsrc)
                        pass
                else:
                    # Not sure where or if they exist
                    # Arp the whole group_no group
                    # Install Drop(hwsrc, hwdst)
                    pass
                    
    def getHostGroup(self, hwaddr):
        return 0

    def knownHost(self, hwaddr):
        """binary search self.known_hosts"""
        return True

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
