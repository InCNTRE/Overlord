# @org InCNTRE 2013
# @author Jonathan Stout

from path import *
from solution import dijkstra
from ...Overlord.Lib.Events import Event, Eventful

class Graph(Eventful):
    def __init__(self):
        Eventful.__init__(self)
        self.path_nodes = {}
        self.paths = {}
        self.switches = {}

        self.path_id = self.id_generator()

        self.add_event("path_down")
        self.add_event("path_mod")
        self.add_event("path_up")

    def add_link(self, rcvr_dpid, sndr_dpid, in_port):
        """
        Adds a directed link to a Switch objects internal link
        structure. Then attempt to recalculate all connections
        with no known path.
        @ param rcvr_dpid Dpid of recieving device
        @ param sndr_dpid Dpid of sending device
        @ param in_port Port number of recieving device
        """
        self.switches[rcvr_dpid].add_link(sndr_dpid, in_port)

        for k in self.paths:
            p = self.paths[k]
            if len(p) is 0:
                new_path = self.get_path(p.start, p.end, p.path_id)
                if p != new_path:
                    self.paths[k] = new_path
                    e = Event()
                    e.path_id = new_path.path_id
                    e.path = []
                    e.new_path = new_path
                    self.handle_event("path_mod", e)

    def add_switch(self, dpid):
        """
        Adds a switch object to the network graph. If the switch
        had already existed, turn up all path_nodes associated
        with dpid.
        @param dpid Dpid of new switch connection
        """
        dpid = str(dpid)
        if dpid in self.switches:
            for p in self.path_nodes:
                self.path_nodes[dpid].node_up()
        else:
            self.switches[dpid] = Switch(dpid)
            self.path_nodes[dpid] = []

    def down_switch(self, dpid):
        """
        Triggers event causing the recalculation of links.
        @param dpid Dpid of device connection that went down
        """
        dpid = str(dpid)
        try:
            for n in self.path_nodes[dpid]:
                n.node_down()
        except KeyError:
            print("No path involoving {} has been provisioned" \
                      .format( str(dpid) ))

    def get_switches(self):
        return self.switches

    def get_path(self, dpid_a, dpid_b, path_id=None):
        """
        Returns a Path object containing PathNodes for
        forwarding rules to be based upon.
        @param dpid_a Dpid of first host device
        @param dpid_b Dpid of second host device
        @param path_id ID of path
        """
        #if not dpid_a in self.switches or not dpid_b in self.switches:
        #    return None

        dpid_a = str(dpid_a)
        dpid_b = str(dpid_b)
        if path_id == None:
            path_id = self.path_id.next()

        # Find a path from all other switches to dpid_a
        pred = dijkstra(self.switches, dpid_a)

        path_of_nodes = []
        if dpid_a in self.switches and dpid_b in self.switches:
            path_of_nodes = self.new_path_nodes(dpid_a, dpid_b, pred)

        #if path_of_nodes == None:
        #    return None

        # Store all nodes by dpid. When a dpid goes down all
        # nodes will be notified of the event.
        path = Path(dpid_a, dpid_b, path_of_nodes)
        for i in range( len(path) ):
            p = path.at(i)
            dpid = p.get_dpid()
            if not dpid in self.path_nodes:
                self.path_nodes[dpid] = []
            self.path_nodes[dpid].append(p)

        # Store all paths by path_id. When a node in a path
        # goes down the path will be notified and send an
        # event to self.handle_path_down or ...path_up.
        path.set_id(path_id)
        path.add_listener("path_down", self.handle_path_down)
        path.add_listener("path_up", self.handle_path_up)
        self.paths[path_id] = path
        return path

    def new_path_nodes(self, dpid_a, dpid_b, pred):
        """
        Recursivly builds an array of PathNodes by storing the
        ingress port, after recieving the predicessor PathNode
        storing the egress port, appending a PathNode to the
        result, and returning.
        @param dpid_a Dpid of first node in the path
        @param dpid_b Dpid of last node in the path
        @param pred A map from a dpid to the predicessor of that dpid
        """
        dpid_a = str(dpid_a)
        dpid_b = str(dpid_b)
        if dpid_a == dpid_b:
            return [PathNode(dpid_a, None, None)]
        elif pred[dpid_b] == -1:
            return []
        else:
            try:
                b_pre = pred[dpid_b]

                i = self.switches[dpid_b].get_link(b_pre).get_port()
                
                nodes = self.new_path_nodes(dpid_a, b_pre, pred)
                
                l_node = nodes[len(nodes)-1]
                
                e = self.switches[l_node.get_dpid()].get_link(dpid_b).get_port()
                l_node.set_egress(e)
                
                nodes.append(PathNode(dpid_b, i, None))
                return nodes
            except KeyError:
                return []

    def handle_path_down(self, e):
        """
        Called when a Path has a node that has gone down. In
        this case we attempt to create a new Path to replace
        the old. If we can we trigger a 'path_mod' event, 
        passing the old and new paths up the listener. else
        we trigger a 'path_down' event with an empty new
        path and the old path.
        @param e Event object from a Path
        @param e.path_id Path ID given to originating Path
        @param e.start First DPID in originating Path
        @param e.end Second DPID in originating Path
        """
        f = Event()
        f.path_id = e.path_id
        f.path = self.paths[e.path_id]
        f.new_path = self.get_path(e.start, e.end, e.path_id)

        if f.new_path == []:
            self.handle_event("path_down", f)
        else:
            self.handle_event("path_mod", f)

    def handle_path_up(self, e):
        """
        Called when a Path has recovered all child path_nodes.
        When this happens the path and path_id are returned
        to the listening class.
        @param e Event object from a Path
        @param e.path_id Path ID given to originating Path
        @param e.start First DPID in originating Path
        @param e.end Second DPID in originating Path
        """
        f = Event()
        f.path_id = e.path_id
        f.start = e.start
        f.end = e.end
        f.path = self.paths[e.path_id]

        self.handle_event("path_up", f)

    def id_generator(self):
        pid = 1
        while True:
            pid += 1
            yield pid

class Switch(object):
    def __init__(self, dpid):
        self.dpid = dpid
        self.links = {}

    # DPID
    def get_dpid(self):
        return self.dpid

    # Links
    def add_link(self, dpid, in_port):
        l = Link(dpid, in_port)
        self.links[dpid] = l

    def get_link(self, dpid):
        return self.links[dpid]

    def get_links(self):
        return self.links

    def remove_link(self, dpid):
        try:
            del(self.links[dpid])
        except KeyError:
            print("WARN::Link does not exist to " + str(dpid))

    def update_link(self, dpid, stats):
        self.links[dpid].update_stats(stats)

    def __str__(self):
        s = "{}::".format(self.dpid)
        for k in self.links:
            s += "{} ".format(str(self.links[k]))
        return s

class Link(object):
    def __init__(self, dpid, port):
        self.dpid = dpid
        self.port = port
        self.stats = {"default" : 1}

        def f (stats): return stats["default"]
        self.weight_func = f

    # DPID
    def get_dpid(self):
        return self.dpid

    # Port
    def get_port(self):
        return self.port

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

    def __str__(self):
        return "{}:{}".format(self.dpid,self.port)
