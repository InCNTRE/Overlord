# @author Jonathan Stout
from pox.core import core

class PatchPanel(object):
    def __init__(self):
        self.patches = {}

    def handle_web_command(self, cmd):
        if u'add_patch' in cmd:
            add_cmd = cmd[u'add_patch']
            self.add_patch(add_cmd['dpid'], add_cmd['port_a'], add_cmd['port_b'])
        elif u'delete_patch' in cmd:
            del_cmd = cmd[u'delete_patch']
            self.delete_patch(del_cmd['patch_id'])
        elif u'modify_patch' in cmd:
            mod_cmd = cmd[u'modify_patch']
            self.modify_patch(mod_cmd['patch_id'], mod_cmd['cmd'])
        else:
            # Unknown or unsupported command
            return

    def add_patch(self, dpid, port_a, port_b):
        patch_id = _id.next()
        virtual_patch = Patch(dpid, port_a, port_b, patch_id)
        flows = virtual_patch.flow_add()
        #TODO::Install flows
        self.patches[patch_id] = virtual_patch
        core.db.save_patch(virtual_patch.get_json())

    def delete_patch(self, patch_id):
        virtual_patch = self.patches[int(patch_id)]
        flows = virtual_patch.flow_delete()
        #TODO::Install flows
        del(self.patches[int(patch_id)])
        core.db.delete_patch(patch.get_json())

    def modify_patch(self, patch_id, cmd):
        """
        Command in format...
        { u'move_port_a' : u'X' } or { u'move_port_b' : u'X'}
        """
        virtual_patch = self.patches[patch_id]
        flows = virtual_patch.flow_delete()
        #TODO::Install flows
        if u'move_port_a' in cmd:
            virtual_patch.port_a = int(cmd[u'move_port_a'])
        if u'move_port_b' in cmd:
            virtual_patch.port_b = int(cmd[u'move_port_b'])
        else:
            # Unknown or unsupported command
            return

        flows = virtual_patch.flow_add()
        #TODO::Install flows
        core.db.update_patch(virtual_patch.get_json())

class Patch(object):
    def __init__(self, dpid, port_a, port_b):
        self.dpid = dpid
        self.port_a = int(port_a)
        self.port_b = int(port_b)

    def flow_add(self):
        flows = {}
        flows[self.dpid] = []

        f = of.ofp_flow_mod()
        f.match.port_no = self.port_a
        f.actions.append(of.ofp_action_output(port=self.port_b))
        flows[self.dpid].append(f)
        
        g = of.ofp_flow_mod()
        g.match.port_no = self.port_b
        f.actions.append(of.ofp_action_output(port=self.port_a))
        flows[self.dpid].append(g)
        return flows

    def flow_delete(self):
        flows = {}
        flows[self.dpid] = []

        f = of.ofp_flow_mod()
        f.match.port_no = self.port_a
        f.command = of.OFPFC_DELETE
        flows[self.dpid].append(f)
        
        g = of.ofp_flow_mod()
        g.match.port_no = self.port_b
        g.command = of.OFPFC_DELETE
        flows[self.dpid].append(g)
        return flows

    def get_json(self):
        return {'dpid': dpid,
                'port_a': port_a,
                'port_b': port_b,
                'patch_id': patch_id}

def id_generator():
    i = 0
    while True:
        i += 1
        yield i

_id = id_generator()
