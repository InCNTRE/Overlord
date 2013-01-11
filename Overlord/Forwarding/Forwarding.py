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
        self.graph = {}
        self.path_nodes = {}
        self.paths = {}

        self.path_id = 0

    def get_path(self, dpid_a, dpid_b, pid=None):
        pred = dijkstra(self.graph, dpid_a)
        path_nodes = self.build_path(dpid_a, dpid_b, pred)

        if pid == None:
            self.path_id += 1
            pid = self.path_id

        path = Path(dpid_a, dpid_b, pid, path_nodes)
        path.add_listener("path_down", self.path_down)
        path.add_listener("path_node_up", self.path_node_up)
        return path

    def path_down(self, e):
        # Remove effected Switch Node from graph
        del( self.graph[e.dpid] )
        #TODO::Remove stale rules
        #
        p = self.get_path(self, e.start, e.end, e.path_id)
        if p != []:
            self.paths[e.path_id] = p
            #TODO::Insert forwarding rules

    def path_node_up(self, e):
        p = self.get_path(self, e.start, e.end, e.path_id)
        if p != p[]:
            self.paths[e.path_id] = p
            #TODO::Insert forwarding rules

    # TODO::Return PathNodes not just dpids
    def build_path(self, dpid_a, dpid_b, pred):
        if dpid_a == dpid_b:
            start_n = PathNode(dpid_a, None, None)
            return [start_n]

        p = pred[dpid_b]
        if p == -1:
            # Path does not exist
            return []
        else:
            n = PathNode(dpid_b, None, None)
            return build_path(dpid_a, p, pred).append(n)

    def Connect(self, log, db, devices, links, host1, host2):
        # Supply third arg to use a better strategy
        #path = links.ResolvePath(host1, host2)
        path = self.get_path(host1["_parent"], host2["_parent"])
        self.paths[path.get_id()] = path

        # The hosts reside on the same switch
        if path == []:
            # host1 -> host2
            fmod = of.ofp_flow_mod(hard_timeout=0)
            fmod.match.dl_src = EthAddr(host1["mac"])
            fmod.match.dl_dst = EthAddr(host2["mac"])
            fmod.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
            # THIS HAS TO CHANGE
            devices.Connection(log, host1["_parent"]).send(fmod)

            fmod = of.ofp_flow_mod(hard_timeout=0)
            fmod.match.dl_src = EthAddr(host2["mac"])
            fmod.match.dl_dst = EthAddr(host1["mac"])
            fmod.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
            # THIS HAS TO CHANGE
            devices.Connection(log, host1["_parent"]).send(fmod)

        log.info("Connected devices: " + str(host1["_name"]) + " and " + str(host2["_name"]))

    def Disconnect(self, log, devices, host):
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
            log.info("Removing flows to disconnect device: " + str(host["_name"]))
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
