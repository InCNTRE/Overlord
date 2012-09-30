# Overlord 2012

from pox.core import core
import pox.openflow.libopenflow_01 as of
import Overlord.Devices as oDev

log = core.getLogger()

devices = None

# def learn_device(pkt):
#     """ learn_device(pkt)
#     Add device information to the database. Everything we can learn,
#     src mac, src ip, in_port, and dpid.
#     """
#     add_device(pkt.src_mac, pkt.src_ip, pkt.in_port, pkt.dpid)
#     push_drop_rule(pkt.src_mac)

# def group_device(name, group_no):
#     """ group_device(name, group_no)
#     Use src_mac and group dst_mac's to build forwarding rules on
#     dpid (when going cross switch be sure to include trunk ports).
#     """
#     push_group_rules(name, group_no)

# def ungroup_device(name, group_no):
#     """ ungroup_device(name, group_no)
#     Destroy all src_mac and dst_mac matches removing the name'd
#     device from the forwarding tables. Replace with drop rules.
#     """
#     src_mac = del_group_rules(name, group_no)
#     push_drop_rule(src_mac)

# def get_message(msg):
#     cmd_parts = overlord.parse_msg(msg)

#     if (cmd_parts.cmd == "ungroup"):
#         pass
#     else if (cmd_parts.cmd == "group"):
#         pass
#     else:
#         pass

def launch():
    # POX Lib
    core.openflow.addListenerByName("ConnectionUp", _handleConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handlePacketIn)
    # Overlord Lib
    #overlord.path_strategy = overlord.simple_forwarding
    global devices
    devices = oDev.Devices()

def _handleConnectionUp(event):
    # msg = of.ofp_flow_mod()
    # msg.actions.append(of.ofp_action_output())
    # event.connection.send(msg)
    pkt = event.parsed
    devices.Learn(pkt)

def _handlePacketIn(event):
    pass
    # packet = event.parsed
    # overlord.learn(packet)

    # if (packet.dst in overlord.known_hosts):
    #     if (overlord.grouped(packet.src, packet.dst)):
    #         overlord.connect(overlord.path_strategy, packet.src, packet.dst)
    #         return True
    # # Install drop action on packet.src or paket.dst
    # msg = of.ofp_flow_mod()
    # msg.match.dl_src = packet.src
    # msg.match.dl_dst = packet.dst
    # event.connection.send(msg)
    # # ARP for unknown packet dst
    # msg = of.arp()
    # msg.dl_src = packet.src
    # msg.dl_dst = 0
    # msg.nw_src = packet.src_ip
    # msg.nw_dst = packet.dst_ip
    # ofp_msg = of.packet_out(msg)
    # event.connection.send(ofp_msg)
    # return False
