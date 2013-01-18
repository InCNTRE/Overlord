# import Overlord.Links
from pox.lib.recoco import Timer

class Links(object):
    """Learn and track network device Links"""
    def __init__(self):
        self.switches = {}
        self.mac_map = {}
        Timer(10, self.handle_timer_tick, recurring = True)

    def handle_timer_tick(self):
        print("Timer just ticked")
        for k in self.switches:
            print("Sending link message to : " + k)

    def Learn(self, event):
        """Called to learn links on every lldp packet in"""
        if str(type(event)) == "<class 'pox.openflow.ConnectionUp'>":
            # Save a connection to this DPID
            self.switches[str(event.dpid)] = event.connection
        else:
            pkt = event.parse()
            
            if pkt.type == 35020:
                self.learnLldp(event, pkt)

    def Forget(self, event):
        try:
            del(self.switches[str(event.dpid)])
        except KeyError:
            pass

    def learnLldp(self, event, pkt):
        lldp_pkt = pkt.next
        pass

    def MakeLLDP(self):
        """Creates an LLDP packet to be sent via packet out
        whenever a new Network Device is discovered"""
        pass
