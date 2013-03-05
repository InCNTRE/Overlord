# @author Jonathan Stout

class Database(object):
    """
    A database abstraction layer.
    """
    def __init__(self):
        pass

    def update_host(self, host):
        """
        Updates the entry found by host.mac with the values found
        in host.
        """
        pass

    def find_host(self, search):
        """
        Returns a single host based on the search dict.
        """
        pass

    def find_hosts(self, search):
        """
        Returns an array of hosts based on the search dict.
        """
        pass
