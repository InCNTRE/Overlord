# import Overlord.Links

class Links(object):
    """Learn and track network device Links"""
    def __init__(self):
        pass

    def Learn(pkt):
        """Called to learn links on every lldp packet in"""
        pass

    def MakeLLDP():
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