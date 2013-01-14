# import Overlord.Forwarding
from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr

import pox.openflow.libopenflow_01 as of

from Graph import *
from Path import *
from PathSolution import dijkstra

class Forwarding(object):
    """Create Forwarding rules for Host to Host communication"""
    def __init__(self):
        self.graph = Graph()
        self.connections = {}

        self.graph.add_listener("path_down", self.path_down)
        self.graph.add_listener("path_mod", self.path_mod)
        self.graph.add_listener("path_up", self.path_up)

    def path_down(self, e):
        c = self.connections[e.path_id]
        self.Disconnect(c.get_host1(), c.get_host2(), e.path)

    def path_mod(self, e):
        c = self.connections[e.path_id]
        self.Disconnect(c.get_host1(), c.get_host2(), e.path)
        self.Connect(c.get_host1(), c.get_host2(), e.new_path)

    def path_up(self, e):
        c = self.connections[e.path_id]
        self.Connect(c.get_host1(), c.get_host2(), e.path)

    def Connect(self, host1, host2, path=None):
        """
        @param host1
        @param host2
        @param path
        """
        # Supply third arg to use a better strategy
        if path == None:
            path = self.graph.get_path(host1["_parent"], host2["_parent"])
        self.connections[path.get_id()] = Connection(path.get_id(), host1, host2)

        # The hosts reside on the same switch
        flows_to_install = {}
        for i in range( len(path) ):
            n = path.at(i)
            dpid = n.get_dpid()

            if not dpid in flows_to_install:
                flows_to_install[dpid] = []

            if n.get_ingress() != None:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host2["mac"])
                fmod.match.dl_src = EthAddr(host1["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(n.get_egress())))
                flows_to_install[dpid].append(fmod)
            else:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host1["mac"])
                fmod.match.dl_src = EthAddr(host2["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
                flows_to_install[dpid].append(fmod)

            if n.get_egress() != None:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host1["mac"])
                fmod.match.dl_src = EthAddr(host2["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(n.ingress())))
                flows_to_install[dpid].append(fmod)
            else:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host2["mac"])
                fmod.match.dl_src = EthAddr(host1["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
                flows_to_install[dpid].append(fmod)

        #devices.Connection(log, host1["_parent"]).send(fmod)
        return flows_to_install

    def Disconnect(self, host1, host2, path):
        conn = devices.Connection(log, host["_parent"])

        # Remove the from host rules
        fmod1 = of.ofp_flow_mod()
        fmod1.match.dl_src = EthAddr(host["mac"])
        fmod1.command = of.OFPFC_DELETE
        # Remove the to host rules
        fmod2 = of.ofp_flow_mod()
        fmod2.match.dl_dst = EthAddr(host["mac"])
        fmod2.command = of.OFPFC_DELETE

        try:
            conn.send(fmod1)
            conn.send(fmod2)
            #log.info("Removing flows to disconnect device: " + str(host["_name"]))
        except AttributeError:
            pass

    def Group(self, log, db, devices, links, host):
        """
        Builds connections between host and all of his group members.
        """
        group_members = db.hosts.find({"group_no": host["group_no"]})
        for h in group_members:
            self.Connect(log, db, devices, links, host, h)

    def Ungroup(self):
        pass
