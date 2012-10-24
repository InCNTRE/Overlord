# import Overlord.Forwarding
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr

class Forwarding(object):
    """Create Forwarding rules for Host to Host communication"""
    def __init__(self):
        pass

    def Connect(self, log, links, event, host1, host2):
        # Supply third arg to use a better strategy
        path = links.ResolvePath(host1, host2)
        
        # The hosts reside on the same switch
        if path == []:
            # host1 -> host2
            fmod = of.ofp_flow_mod(idle_timeout=600)
            fmod.match.dl_src = EthAddr(host1["mac"])
            fmod.match.dl_type = 0x0800
            fmod.match.nw_dst = IPAddr(str(host2["ip"]))
            fmod.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
            event.connection.send(fmod)
            # host2 -> host1
            fmod = of.ofp_flow_mod(idle_timeout=600)
            fmod.match.dl_src = EthAddr(host2["mac"])
            fmod.match.dl_type = 0x0800
            fmod.match.nw_dst = IPAddr(str(host1["ip"]))
            fmod.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
            event.connection.send(fmod)

    def Disconnect(self, host1, host2):
        pass

    def Group(self):
        pass

    def Ungroup(self):
        pass
