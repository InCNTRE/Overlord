# import Overlord.Devices
import inspect

class Devices(object):
    """Learn and track Network Devices"""
    def __init__(self):
        self.dpids = []

    def Learn(self, log, event):
        """Learn dpid and ports"""
        # If a Features reply
        if str(type(event)) == "<class 'pox.openflow.ConnectionUp'>":
            log.debug('Learnt dpid: ' + str(event.dpid))
            self.memorizeDpid(event.dpid)
            self.memorizePorts(event.dpid, event.ofp.ports)
        # Else If a Port Status Up

        # Else if a Port Status Down

        # Else don't do anything
        # Make sure dpids are saved inorder
        log.debug(self.dpids)
        
    def memorizeDpid(self, dpid):
        """ Basically insertionSort I won't have more
        than 20 switches at a time connected anyway.
        this is local only."""
        i = 0
        while i < len(self.dpids) and dpid > self.dpids[i]:
            i += 1
        self.dpids.insert(i, dpid)

    def memorizePorts(self, dpid, ports):
        """ Publishes all ports to a database. The
        inverse of this function 'forgetPorts' removes
        ports from the database. When either is called
        links involving these ports should re-learnt."""
        pass
