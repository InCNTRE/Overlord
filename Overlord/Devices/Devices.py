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

    # Register fwding with core so no need to pass fwding and links
    def Learn(self, log, db, event, fwding=None, lnks=None):
        """
        Learn dpid and ports
        """
        if str(type(event)) == "<class 'pox.openflow.ConnectionUp'>":
            """
            Save devices locally and in the db. Search for device first
            in case any meta data had been created for the device on a
            previous launch.
            """
            dpid = str(event.dpid)
            self.switches[dpid] = event.connection
            d = db.devices.find_one({'dpid': dpid})
            if d is None:
                d = {}
            d["dpid"] = dpid
            db.devices.save(d)
            log.info("Connected to switch: " + dpid)

            # Delete any existing flows in the switch.
            msg = of.ofp_flow_mod()
            msg.command = of.OFPFC_DELETE
            event.connection.send(msg)

            # Make switch forward all ARP to Overlord.
            msg = of.ofp_flow_mod()
            msg.match.dl_type = 0x0806
            msg.priority = 40000
            msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
            event.connection.send(msg)

            # Attempt to group all hosts connected to dpid
            if fwding != None and lnks != None:
                log.info("Building host links in line with database.")
                hosts = db.hosts.find({'_parent': dpid})
                for h in hosts:
                    if h['group_no'] != '-1':
                        fwding.Group(log, db, self, lnks, h)
                                    
        elif str(type(event)) == "<class 'pox.openflow.PortStatus'>":
            log.debug('Updating port information.')
            self.relearnPorts(event)

    def Forget(self, log, event):
        try:
            del(self.switches[str(event.dpid)])
            log.info("Lost connection to switch: " + str(event.dpid))
        except KeyError:
            log.error("Tried to delete nonexistent Switch from memory")
        
    def AllConnections(self):
        return self.switches

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
