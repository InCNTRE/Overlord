# import Overlord.Forwarding
from pox.core import core
from pox.lib.addresses import EthAddr, IPAddr

import pox.openflow.libopenflow_01 as of

from Graph import *
from Path import *
from PathSolution import dijkstra
from ..Lib.Events import Event, Eventful

class Forwarding(Eventful):
    """Create Forwarding rules for Host to Host communication"""
    def __init__(self):
        self.graph = Graph()
        self.connections = {}

        self.add_event("new_flows")

        self.graph.add_listener("path_down", self.path_down)
        self.graph.add_listener("path_mod", self.path_mod)
        self.graph.add_listener("path_up", self.path_up)

    def add_link(self, in_dpid, in_port, org_dpid):
        self.graph.add_link(in_dpid, org_dpid, in_port)

    def Learn(self, event):
        self.graph.add_switch(str(event.dpid))
        
    def Forget(self, event):
        self.graph.down_switch(str(event.dpid))

    def path_down(self, e):
        c = self.connections[e.path_id]
        flows1 = self.CleanupPath(c.get_host1(), e.path)
        if flows1 != {}:
            e = Event()
            e.flows = flows1
            self.handle_event("new_flows", e)
        flows2 = self.CleanupPath(c.get_host2(), e.path)
        if flows2 != {}:
            e = Event()
            e.flows = flows2
            self.handle_event("new_flows", e)

    def path_mod(self, e):
        c = self.connections[e.path_id]
        flows1 = self.CleanupPath(c.get_host1(), e.path)
        if flows1 != {}:
            e = Event()
            e.flows = flows1
            self.handle_event("new_flows", e)
        flows2 = self.CleanupPath(c.get_host2(), e.path)
        if flows2 != {}:
            e = Event()
            e.flows = flows2
            self.handle_event("new_flows", e)
        flows3 = self.Connect(c.get_host1(), c.get_host2(), e.new_path)
        if flows3 != {}:
            e = Event()
            e.flows = flows3
            self.handle_event("new_flows", e)

    def path_up(self, e):
        c = self.connections[e.path_id]
        flows = self.Connect(c.get_host1(), c.get_host2(), e.path)
        if flows != {}:
            e = Event()
            e.flows = flows
            self.handle_event("new_flows", e)

    def Connect(self, host1, host2, path=None):
        """
        Build a connection based on either @path or a new path
        found between host1's parent and host2's parent.
        @param host1
        @param host2
        @param path
        """
        if path == None:
            path = self.graph.get_path(host1["_parent"], host2["_parent"])

        self.connections[path.get_id()] = Connection(path.get_id(), host1, host2)

        flows_to_install = {}
        for i in range( len(path) ):
            n = path.at(i)
            dpid = n.get_dpid()

            if not dpid in flows_to_install:
                flows_to_install[dpid] = []

            if n.get_ingress() == None and n.get_egress() == None:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host2["mac"])
                fmod.match.dl_src = EthAddr(host1["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
                flows_to_install[dpid].append(fmod)

                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host1["mac"])
                fmod.match.dl_src = EthAddr(host2["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
                flows_to_install[dpid].append(fmod)
            elif n.get_ingress() == None and n.get_egress() != None:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host2["mac"])
                fmod.match.dl_src = EthAddr(host1["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(n.get_egress())))
                flows_to_install[dpid].append(fmod)

                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host1["mac"])
                fmod.match.dl_src = EthAddr(host2["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
                flows_to_install[dpid].append(fmod)
            elif n.get_ingress() != None and n.get_egress() == None:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host2["mac"])
                fmod.match.dl_src = EthAddr(host1["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
                flows_to_install[dpid].append(fmod)

                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host1["mac"])
                fmod.match.dl_src = EthAddr(host2["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(n.get_ingress())))
                flows_to_install[dpid].append(fmod)
            elif n.get_ingress() != None and n.get_egress() != None:
                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host2["mac"])
                fmod.match.dl_src = EthAddr(host1["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(n.get_egress())))
                flows_to_install[dpid].append(fmod)

                fmod = of.ofp_flow_mod(hard_timeout=0)
                fmod.match.dl_dst = EthAddr(host1["mac"])
                fmod.match.dl_src = EthAddr(host2["mac"])
                fmod.actions.append(of.ofp_action_output(port=int(n.get_ingress())))
                flows_to_install[dpid].append(fmod)
            else:
                print("ERROR::This should not have happened.")

        return flows_to_install

    def Disconnect(self, host):
        #conn = devices.Connection(log, host["_parent"])

        # Remove the from host rules
        fmod1 = of.ofp_flow_mod()
        fmod1.match.dl_src = EthAddr(host["mac"])
        fmod1.command = of.OFPFC_DELETE
        
        # Remove the to host rules
        fmod2 = of.ofp_flow_mod()
        fmod2.match.dl_dst = EthAddr(host["mac"])
        fmod2.command = of.OFPFC_DELETE
        flows = [fmod1, fmod2] 
        return flows

    def CleanupPath(self, host, path):
        flows_to_install = {}

        for i in range( len(path) ):
            dpid = path.at(i).get_dpid()
            if not dpid in flows_to_install:
                flows_to_install[dpid] = []

            # Remove the from host rules
            fmod1 = of.ofp_flow_mod()
            fmod1.match.dl_src = EthAddr(host["mac"])
            fmod1.command = of.OFPFC_DELETE
            
            # Remove the to host rules
            fmod2 = of.ofp_flow_mod()
            fmod2.match.dl_dst = EthAddr(host["mac"])
            fmod2.command = of.OFPFC_DELETE
            flows_to_install[dpid] = [fmod1, fmod2]
        return flows_to_install

    def Group(self, log, db, devices, links, host):
        """
        Builds connections between host and all of his group members.
        """
        ungroupables = []
        group_members = db.hosts.find({"group_no": host["group_no"]})
        #print("Members: {}".format(group_members))
        for h in group_members:
            #print(h)
            #self.Connect(log, db, devices, links, host, h)
            flows = self.Connect(host, h)
            if flows != None:
                print("Grouping host: {}".format(h))
                for k in flows:
                    for f in flows[k]:
                        devices.Connection(log, k).send(f)
            else:
                # h could not be connected to host
                #if h["mac"] != host["mac"]:
                    #print("Adding {} and {}".format(h["mac"], host["mac"]))
                ungroupables.append(h)
        return ungroupables

    def Ungroup(self):
        pass

class Connection(object):
    def __init__(self, path_id, host1, host2):
        self.path_id = path_id
        self.host1 = host1
        self.host2 = host2

    def get_host1(self):
        return self.host1

    def get_host2(self):
        return self.host2

    def get_id(self):
        return self.path_id
