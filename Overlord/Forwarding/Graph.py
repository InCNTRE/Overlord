# @org InCNTRE 2013
# @author Jonathan Stout    

from Path import *
from PathSolution import dijkstra
from ..Lib.Events import Event, Eventful

class Graph(Eventful):
    def __init__(self):
        self.path_nodes = {}
        self.paths = {}
        self.switches = {}

        self.path_id = self.id_generator()

        self.add_event("path_down", self.handle_path_down)
        self.add_event("path_mod", self.handle_path_mod)
        self.add_event("path_up", self.handle_path_up)

    def add_link(self, rcvr_dpid, sndr_dpid, in_port):
        """
        Adds a link to a Switch objects internal link structure.
        @ param rcvr_dpid Dpid of recieving device
        @ param sndr_dpid Dpid of sending device
        @ param in_port Port number of recieving device
        """
        self.switches[rcvr_dpid].add_link(sndr_dpid, in_port)

    def add_switch(self, dpid):
        """
        Adds a switch object to the network graph.
        @param dpid Dpid of new switch connection
        """
        self.switches[dpid] = Switch(dpid)

    def down_switch(self, dpid):
        """
        Triggers event causing the recalculation of links.
        @param dpid Dpid of device connection that went down
        """
        try:
            self.path_nodes[dpid].node_down()
        except KeyError:
            print("No path involoving {} has been provisioned" \
                      .format( str(dpid) ))

    def get_path(self, dpid_a, dpid_b, path_id=None):
        """
        Returns a Path object containing PathNodes for
        forwarding rules to be based upon.
        @param dpid_a Dpid of first host device
        @param dpid_b Dpid of second host device
        @param path_id ID of path
        """
        #TODO:: Update this code to build path
        if path_id == None:
            path_id = self.path_id

    def id_generator(self):
        pid = 1
        while True:
            pid += 1
            yield pid

    def handle_path_down(self, e):
        pass

    def handle_path_mod(self, e):
        pass

    def handle_path_up(self, e):
        pass

class Switch(object):
    def __init__(self, dpid):
        self.dpid = dpid
        self.links = {}

    # DPID
    def get_dpid(self):
        return self.dpid

    # Links
    def add_link(self, dpid, in_port):
        l = Link(in_port)
        self.links[dpid] = l

    def get_links(self):
        return self.links

    def remove_link(self, dpid):
        try:
            del(self.links[dpid])
        except KeyError:
            print("WARN::Link does not exist to " + str(dpid))

    def update_link(self, dpid, stats):
        self.links[dpid].update_stats(stats)

class Link(object):
    def __init__(self, dpid, in_port):
        self.dpid = dpid
        self.port = in_port
        self.stats = {"default" : 1}

        def f (stats): return stats["default"]
        self.weight_func = f

    # DPID
    def get_dpid(self):
        return self.dpid

    # Port
    def get_port(self):
        return self.in_port

    # Stats
    def get_stats(self):
        return self.stats

    def update_stats(self, stats):
        self.stats = stats

    # Weight
    def get_weight(self):
        return self.weight_func(self.stats)

    def set_weight_function(self, f):
        self.weight_func = f

