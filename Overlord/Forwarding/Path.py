# @org InCNTRE 2013
# @author Jonathan Stout

from ..Lib.Events import Event, Eventful

class Path(Eventful):
    def __init__(self, start, end, path):
        Eventful.__init__(self)
        self.path = path
        self.path_id = -1
        self.start = start
        self.end = end

        # Register event so module above knows to attempt, or not
        # recalculation of path.
        self.add_event("path_down")
        self.add_event("path_up")

        # Add listener to each Node
        for p in self.path:
            p.add_listener("down", self.handle_node_down)
            p.add_listener("up", self.handle_node_up)

    def __eq__(self, o):
        if isinstance(o, Path):
            if self.path != o.path:
                return False
            if self.start != o.start:
                return False
            if self.end != o.end:
                return False
            return True
        else:
            return False

    def get_nodes(self):
        return self.path

    def all_nodes_up(self):
        for p in self.path:
            if not p.is_up():
                return False
        return True

    def __len__(self):
        return len(self.path)

    def get_id(self):
        return self.path_id

    def set_id(self, path_id):
        self.path_id = path_id

    def at(self, i):
        return self.path[i]

    def handle_node_up(self, e):
        if self.all_nodes_up():
            f = Event()
            f.dpid = e.dpid
            f.path_id = self.path_id
            f.start = self.start
            f.end = self.end
            
            print("WARN::Node in path came back up. Connection may be recovered.")
            self.handle_event("path_up", f)

    def handle_node_down(self, e):
        f = Event()
        f.dpid = e.dpid
        f.path_id = self.path_id
        f.start = self.start
        f.end = self.end

        print("WARN::Node in path went down. A new path must be calculated.")
        self.handle_event("path_down", f)

class PathNode(Eventful):
    def __init__(self, dpid, ingress, egress):
        Eventful.__init__(self)
        self.dpid = dpid
        self.ingress = ingress
        self.egress = egress
        self.up = True

        self.add_event("down")
        self.add_event("up")

    def __str__(self):
        s = "DPID:{} INGRESS:{} EGRESS:{} UP:{}".format(self.dpid, self.ingress, self.egress, self.up)
        return s

    def __eq__(self, o):
        if isinstance(o, PathNode):
            if self.dpid != o.dpid:
                return False
            if self.ingress != o.ingress:
                return False
            if self.egress != o.egress:
                return False
            if self.up != o.up:
                return False
            return True
        else:
            return False

    def __ne__(self, o):
        return not self.__eq__(o)

    def get_dpid(self):
        return self.dpid

    def get_ingress(self):
        return self.ingress

    def get_egress(self):
        return self.egress

    def set_egress(self, port_no):
        self.egress = port_no

    def is_up(self):
        return self.up

    def node_up(self):
        self.up = True
        e = Event()
        e.dpid = self.dpid
        self.handle_event("up", e)

    def node_down(self):
        self.up = False
        e = Event()
        e.dpid = self.dpid
        self.handle_event("down", e)
