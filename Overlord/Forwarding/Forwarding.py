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
            #fmod.match.dl_dst = EthAddr(host2["mac"])
            fmod.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
            event.connection.send(fmod)
            # host2 -> host1
            fmod = of.ofp_flow_mod(idle_timeout=600)
            fmod.match.dl_src = EthAddr(host2["mac"])
            fmod.match.dl_type = 0x0800
            fmod.match.nw_dst = IPAddr(str(host1["ip"]))
            #fmod.match.dl_dst = EthAddr(host1["mac"])
            fmod.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
            event.connection.send(fmod)

            #forward arp too :P. When I move to RPC calls remove this and
            # match on dl_src and dl_dst
            msg = of.ofp_flow_mod(idle_timeout=5)
            msg.match.dl_src = EthAddr(host1["mac"])#arp_pkt.hwsrc
            msg.match.dl_type = 0x0806
            msg.match.dl_dst = EthAddr(host2["mac"])#arp_pkt.hwdst
            msg.actions.append(of.ofp_action_output(port=int(host2["port_no"])))
            event.connection.send(msg)

            msg = of.ofp_flow_mod(idle_timeout=5)
            #msg.match.dl_src = arp_pkt.hwsrc
            msg.match.dl_src = EthAddr(host2["mac"])#arp_pkt.hwsrc
            msg.match.dl_type = 0x0806
            #msg.match.protodst = arp_pkt.protodst
            msg.match.dl_dst = EthAddr(host1["mac"])#arp_pkt.hwdst
            msg.actions.append(of.ofp_action_output(port=int(host1["port_no"])))
            event.connection.send(msg)

        log.info("Adding flows to connect devices: " + str(host1["_name"]) + " and " + str(host2["_name"]))

    def Disconnect(self, log, devices, host):
        conn = devices.Connection(host["_parent"])

        # Remove the from host rules
        fmod = of.ofp_flow_mod()
        fmod.match.dl_src = EthAddr(host["mac"])
        fmod.command = of.OFPFC_DELETE
        conn.send(fmod)

        # Remove the to host rules
        fmod = of.ofp_flow_mod()
        fmod.match.dl_type = 0x0800
        fmod.match.nw_dst = IPAddr(str(host["ip"]))
        #fmod.match.dl_dst = EthAddr(host["mac"])
        fmod.command = of.OFPFC_DELETE
        conn.send(fmod)

        fmod = of.ofp_flow_mod()
        fmod.match.dl_type = 0x0806
        #fmod.match.nw_dst = IPAddr(str(host["ip"]))
        fmod.match.dl_dst = EthAddr(host["mac"])
        fmod.command = of.OFPFC_DELETE
        conn.send(fmod)
        
        fmod = of.ofp_flow_mod()
        fmod.match.dl_type = 0x0806
        #fmod.match.nw_dst = IPAddr(str(host["ip"]))
        fmod.match.dl_dst = EthAddr(host["mac"])
        fmod.command = of.OFPFC_DELETE
        conn.send(fmod)

        log.info("Removing flows to disconnect device: " + str(host["_name"]))

    def Group(self):
        pass

    def Ungroup(self):
        pass
