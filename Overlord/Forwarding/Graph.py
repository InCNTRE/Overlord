# @org InCNTRE 2013
# @author Jonathan Stout    

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

