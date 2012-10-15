# import Overlord.Links

class Links(object):
    """Learn and track network device Links"""
    def __init__(self):
        pass

    def Learn(self, log, event):
        """Called to learn links on every lldp packet in"""
        pkt = event.parse()

        if pkt.type == 35020:
            self.learnLldp(event, pkt)

    def learnLldp(self, event, pkt):
        lldp_pkt = pkt.next
        pass

    def MakeLLDP(self):
        """Creates an LLDP packet to be sent via packet out
        whenever a new Network Device is discovered"""
        pass

    def ResolvePath(self, host1, host2, strategy=None):
        if strategy == None:
        elif host1.dpid == host2.dpid:
            return []
        else:
            # Find a valid path. Don't worry about anything else.
            return None