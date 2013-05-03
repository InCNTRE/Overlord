# @author Jonathan Stout
from pymongo import Connection

class Database(object):
    """
    A database abstraction layer. Connects to address if
    specified, else assumes a local connection.
    @arg address - A string in form ip_address:port
    """
    def __init__(self, address=None):
        if address is None:
            conn = Connection()
            self.db = conn['overlord']
        # TODO: Add remote connection option.

        if "messages" in self.db.collection_names():
            self.db["messages"].drop()
            self.db.create_collection("messages", size=100000, max=100, capped=True)
            self.db.messages.insert({"message": "null"})
            self.last_event = -1
        
    def get_connection(self):
        return self.db

    def find_device(self, search):
        """
        Returns a single Device based on the search dict.
        """
        return self.db.devices.find_one(search)

    def find_devices(self, search):
        """
        Returns an array of Devices based on the search dict.
        """
        return self.db.devices.find(search)

    def update_device(self, device):
        """
        Updates the entry found by device.dpid with the values found
        in device.
        """
        spec = {"dpid": device["dpid"]}
        if self.find_device(spec) != None:
            print("Updating Device %s" % str(device['dpid']))
            self.db.devices.update(spec, {"$set": device})
        else:
            self.db.devices.insert(device)

        self.db.devices.update(spec, {"$set": device})

    def find_event(self, search):
        """
        Finds the latest command added to the database.
        """
        try:
            latest = self.db.messages.find_one({"_id": {"$gt": self.last_event}})
            self.last_event = latest["_id"]
        except KeyError:
            # No messages available
            return None

    def find_host(self, search):
        """
        Returns a single Host based on the search dict.
        """
        return self.db.hosts.find_one(search)

    def find_hosts(self, search):
        """
        Returns an array of Hosts based on the search dict.
        """
        return self.db.hosts.find(search)

    def update_host(self, host):
        """
        Updates the entry found by host.mac with the values found
        in host.
        """
        spec = {"mac": host["mac"]}
        if self.find_host(spec) != None:
            print("Updating Host %s" % str(host["mac"]))
            self.db.hosts.update(spec, {"$set": host})
        else:
            self.db.hosts.insert(host)
        
    def find_patch(self, search):
        """
        Returns a single Patch based on the search dict.
        """
        return self.db.patches.find_one(search)

    def find_patches(self, search):
        """
        Returns an array of Patches based on the search dict.
        """
        return self.db.hosts.find(search)

    def update_patch(self, patch):
        """
        Updates the entry found by host.mac with the values found
        in host.
        """
        spec = {u'patch_id': patch['patch_id']}
        if self.find_patch(spec) != None:
            print("Updating Patch %s" % str(host['patch_id']))
            self.db.patches.update(spec, {"$set": patch})
        else:
            self.db.patches.insert(patch)
