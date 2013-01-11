# @org InCNTRE 2013
# @author Jonathan Stout

from ..Lib.Events import Event, Eventful

class Path(Eventful):
    def __init__(self, start, end, pid, path):
        Eventful.__init__(self)
        self.path = path
        self.path_id = pid
        self.start = start
        self.end = end

        # Register event so module above knows to attempt, or not
        # recalculation of path.
        self.add_event("path_down")
        self.add_event("path_node_up")

        # Add listener to each Node
        for p in self.path:
            p.add_listener("down", self.handle_node_down)
            p.add_listener("up", self.handle_node_up)

    def __len__(self):
        return len(self.path)

    def get_id(self):
        return self.path_id

    def at(self, i):
        return self.path[i]

    def handle_node_up(self, e):
        f = Event()
        f.dpid = e.dpid
        f.path_id = self.path_id
        f.start = self.start
        f.end = self.end

        print("WARN::Node in path came back up. Connection may be recovered.")
        self.handle_event("path_node_up", f)

    def handle_node_down(self, e):
        f = Event()
        f.dpid = e.dpid
        f.path_id = self.path_id
        f.start = self.start
        f.end = self.end

        print("WARN::Node in path went down. Connection may be recovered.")
        self.handle_event("path_down", f)

class PathNode(Eventful):
    def __init__(self, dpid, ingress, egress):
        Eventful.__init__(self)
        self.dpid = dpid
        self.ingress = ingress
        self.egress = egress

        self.add_event("down")
        self.add_event("up")

    def get_dpid(self):
        return self.dpid

    def get_ingress(self):
        return self.ingress

    def get_egress(self):
        return self.egress

    def node_up(self):
        e = Event()
        e.dpid = self.dpid
        self.handle_event("up", e)

    def node_down(self):
        e = Event()
        e.dpid = self.dpid
        self.handle_event("down", e)
