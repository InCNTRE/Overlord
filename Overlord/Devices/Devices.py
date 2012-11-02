# Overlord.Devices
# Jonathan M. Stout 2012
#
# Usage
# from Overlord.Devices import Devices as oDev
# devices = oDev.Devices()
import pox.openflow.libopenflow_01 as of

class Devices(object):
    """
    Learn and track Network Devices
    """
    def __init__(self):
        self.switches = {}

    def Learn(self, log, db, event):
        """
        Learn dpid and ports
        """
        if str(type(event)) == "<class 'pox.openflow.ConnectionUp'>":
            """
            Save devices locally and in the db. Search for device first
            in case any meta data had been created for the device on a
            previous launch.
            """
            self.switches[str(event.dpid)] = event.connection
            d = db.devices.find_one({'dpid': str(event.dpid)})
            if d is None:
                d = {}
            d["dpid"] = str(event.dpid)
            db.devices.save(d)
            log.info("Connected to switch: " + str(event.dpid))
            # Install high priority rule to catch all arp
            msg = of.ofp_flow_mod()
            msg.match.dl_type = 0x0806
            msg.priority = 40000
            msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
            event.connection.send(msg)
        elif str(type(event)) == "<class 'pox.openflow.PortStatus'>":
            log.debug('Updating port information.')
            self.relearnPorts(event)

    def Forget(self, log, event):
        try:
            del(self.switches[str(event.dpid)])
            log.info("Lost connection to switch: " + str(event.dpid))
        except KeyError:
            log.error("Tried to delete nonexistent Switch from memory")
        
    def Connection(self, log, dpid):
        try:
            return self.switches[str(dpid)]
        except KeyError:
            log.error("Could not find a Connection for desired Device.")

    def memorizePorts(self, dpid, ports):
        """ Publishes all ports to a database."""
        pass

    def relearnPorts(self, event):
        """ Publishes port updates to a database.
        Links involving these ports should be
        relearnt."""
        pass
