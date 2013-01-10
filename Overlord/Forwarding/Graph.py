# @org InCNTRE 2013
# @author Jonathan Stout    

class Switch(object):
    def __init__(self, dpid):
        self.dpid = dpid
        self.links = {}

    def add_link(self, dpid, in_port):
        l = Link(in_port)
        self.links[dpid] = l

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

        # Weight function
        def f (stats): return stats["default"]
        self.set_weight_function(f)

    def get_weight(self):
        return self.calc_weight(self.stats)

    def set_weight_function(self, f):
        self.calc_weight = f

    def update_stats(self, stats):
        self.stats = stats

    def get_dpid(self):
        return self.dpid

    def get__port(self):
        return self.in_port

    def get_stats(self):
        return self.stats
