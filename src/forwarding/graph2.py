from path import *
from solution import dijkstra
from ..util.events import Event, Eventful

class Graph(Eventful):
    def __init__(self):
        Eventful.__init__(self)
        self.links = {}
        self.paths = {}
        self.path_nodes = {}
        self.path_id = self.id_generator()

        self.add_event("path_down")
        self.add_event("path_mod")
        self.add_event("path_up")

    def add_link(self, dpid_in, dpid_out, port_in):
        if dpid_in not in self.links:
            self.links[dpid_in] = {}
        if dpid_out not in self.links[dpid_in]:
            self.links[dpid_in][dpid_out] = port_in

    def remove_node(self, dpid):
        for k in self.links:
            for l in self.links[k]:
                if l == dpid:
                    del(self.links[k][l])
            if k == dpid:
                del(self.links[k])
        for k, v in self.path_nodes.iteritems():
            if k == dpid:
                v.is_down()
        
