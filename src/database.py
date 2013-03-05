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

    def find_device(self, search):
        """
        Returns a single Device based on the search dict.
        """
        pass

    def find_devices(self, search):
        """
        Returns an array of Devices based on the search dict.
        """
        pass

    def update_device(self, device):
        """
        Updates the entry found by device.dpid with the values found
        in device.
        """
        pass

    def find_event(self, search):
        """
        Finds the latest command added to the database.
        """
        pass

    def find_host(self, search):
        """
        Returns a single Host based on the search dict.
        """
        pass

    def find_hosts(self, search):
        """
        Returns an array of Hosts based on the search dict.
        """
        pass

    def update_host(self, host):
        """
        Updates the entry found by host.mac with the values found
        in host.
        """
        pass
