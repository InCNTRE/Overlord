# @org InCNTRE 2013
# @author Jonathan Stout

from ..Lib.Events import Event, Eventful

class Path(Eventful):
    def __init__(self, start, end, path):
        Eventful.__init__(self)
        self.path = path
        self.start = start
        self.end = end

        # Register event so module above knows to attempt, or not,
        # recalculation of path.
        self.add_event("path_down")
        self.add_event("path_failure")

        # Add listener to each Node
        for p in self.path:
            p.add_listener("down", self.handle_node_down)

    def __len__(self):
        return len(self.path)

    def at(self, i):
        return self.path[i]

    def handle_node_down(self, e):
        f = Event()
        f.start = self.start
        f.end = self.end

        if e.dpid == self.start or e.dpid == self.end:
            print("ERROR::End Node went down. End hosts cannot communicate.")
            self.handle_event("path_failure", f)
        else:
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
