# @org InCNTRE 2013
# @author Jonathan Stout

def dict_sort(i):
    """
    Used as @key by min() to sort dict.items()
    by value.
    @param i A tuple in form of (key, value)
    """
    return i[1]

def dijkstra(graph, start):
    q = {}
    dist = {}
    pred = {}

    for v in graph:
        dpid = graph[v].get_dpid()
        dist[dpid] = 999
        pred[dpid] = -1
    dist[start] = 0

    for v in graph:
        dpid = graph[v].get_dpid()
        q[dpid] = dist[dpid]

    while len(q) != 0:
        # u is a dpid
        u = min(q.items(), key=dict_sort)[0]

        # v is u's neighbor as a Link object
        links = graph[u].get_links()
        for k in links:
            w = links[k].get_weight()

            new_len = dist[u] + w
            dpid = links[k].get_dpid()
            if new_len < dist[dpid]:
                q[dpid] = new_len
                dist[dpid] = new_len
                pred[dpid] = u
        del(q[u])

    return pred
