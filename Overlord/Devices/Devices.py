# Overlord.Devices
# Jonathan M. Stout 2012
#
# Usage
# from Overlord.Devices import Devices as oDev
# devices = oDev.Devices()

import inspect

class Devices(object):
    """Learn and track Network Devices"""
    def __init__(self):
        self.switches = {}
        self.dpids = []

    def Learn(self, log, event):
        """Learn dpid and ports"""
        log.debug(event)
        # If a Features reply
        if str(type(event)) == "<class 'pox.openflow.ConnectionUp'>":
            log.debug('Learnt dpid: ' + str(event.dpid))
            self.memorizeDpid(event.dpid)
            self.memorizePorts(event.dpid, event.ofp.ports)
        elif str(type(event)) == "<class 'pox.openflow.PortStatus'>":
            log.debug('Updating port information.')
            self.relearnPorts(event)
        
    def memorizeDpid(self, dpid):
        """ Basically insertionSort I won't have more
        than 20 switches at a time connected anyway.
        this is local only."""
        i = 0
        while i < len(self.dpids) and dpid > self.dpids[i]:
            i += 1
        self.dpids.insert(i, dpid)

    def memorizePorts(self, dpid, ports):
        """ Publishes all ports to a database."""
        pass

    def relearnPorts(self, event):
        """ Publishes port updates to a database.
        Links involving these ports should be
        relearnt."""
        pass
