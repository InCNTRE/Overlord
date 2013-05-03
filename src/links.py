from pox.core import core
from pox.lib.recoco import Timer
from pox.lib.addresses import EthAddr
from pox.lib.packet.ethernet import ethernet
import pox.openflow.libopenflow_01 as of

class Links(object):
    """Learn and track network device Links"""
    def __init__(self):
        self.switches = {}
        self.mac_map = {}
        Timer(10, self.handle_timer_tick, recurring = True)

    def handle_timer_tick(self):
        #print("Timer just ticked")
        for k in self.mac_map:
            pkt = ethernet()
            pkt.src = EthAddr(k)
            pkt.type = 0x0ff1
            
            pkt_out = of.ofp_packet_out()
            act = of.ofp_action_output(port=of.OFPP_FLOOD)
            pkt_out.actions.append(act)
            pkt_out.data = pkt
            self.switches[self.mac_map[k]].send(pkt_out)
            #print("mac: {} dpid: {}".format(k, self.mac_map[k]))

    def get_mac(self, dpid_string):
        e = EthAddr(int(dpid_string))
        if not e in self.mac_map:
            self.mac_map[e.toInt()] = dpid_string
        return e.toInt()

    def Learn(self, event):
        """Called to learn links on every lldp packet in"""
        if str(type(event)) == "<class 'pox.openflow.ConnectionUp'>":
            # Save a connection to this DPID
            self.switches[str(event.dpid)] = event.connection
            # Insert rule to packet_in all packets
            # with EthAddr == 0x0ff1
            self.get_mac(str(event.dpid))            
        else:
            pkt = event.parse()
            
            if pkt.type == 0x0ff1:
                return self.learnLldp(event, pkt)
        return None

    def Forget(self, event):
        try:
            del(self.switches[str(event.dpid)])
        except KeyError:
            pass

    def learnLldp(self, event, pkt):
        """
        Returns
        (event.dpid, event.in_port, self.mac_map[pkt.src.toInt()])
        """
        #print("LINK_MSG FROM {} port {} Origin {}".format(str(event.dpid), str(event.port), self.mac_map[pkt.src.toInt()]))
        if core.devices.Connection(None,event.dpid):
            return (str(event.dpid), str(event.port), self.mac_map[pkt.src.toInt()])
