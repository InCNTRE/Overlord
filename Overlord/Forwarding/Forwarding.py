# import Overlord.Forwarding

class Forwarding(object):
    """Create Forwarding rules for Host to Host communication"""
    def __init__(self):
        pass

    def Connect(host1, host2):
        # Supply third arg to use a better strategy
        path = links.ResolvePath(host1, host2)
        
        # The hosts reside on the same switch
        if path == []:
            # host1 -> host2
            fmod = of.ofp_flow_mod(idle_timeout=3)
            fmod.match.dl_src = host1.mac
            fmod.match.dl_dst = host2.mac
            fmod.action = of.ofp_action_output(port = host2.port)
            event.connection.send(fmod)
            # host2 -> host1
            fmod.match.dl_src = host2.mac
            fmod.match.dl_dst = host1.mac
            fmod.action = of.ofp_action_output(port = host1.port)
            event.connection.send(fmod)

    def Disconnect(host1, host2):
        pass

    def Group():
        pass

    def Ungroup():
        pass
