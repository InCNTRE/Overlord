""" Jonathan M. Stout 2012
OverlordMessage.py
Event and Event Raising Classes from the web front-end.
"""
from pox.core import core
import time
from pox.lib.revent.revent import EventMixin, Event

class WebCommand(Event):
    """
    A WebCommand Event is any event raised by the
    web front-end.
    """
    def __init__(self, command):
        Event.__init__(self)
        self.command = command
        
    def Command(self):
        return self.command

class OverlordMessage(EventMixin):
    """
    EventMixin class for raising custom events to the
    overlord classes.
    """
    _eventMixin_events = set([WebCommand])
    
    def __init__(self):
        EventMixin.__init__(self)

    def run(self):
        """
        Not the best way to get events from the web front-end.
        I'd prefer using something like redis in the future.
        We find the last '_id' in the database and save it for
        the next iteration to save on search time. If the
        collection is empty sleep.
        """
        latest = core.db.get_connection().messages.find({}, await_data=True, tailable=True).sort("$natural", 1).limit(1)
        
        try:
            last = None
            while True:
                try:
                    cmd = latest.next()
                    last = cmd["_id"]
                    # Raise Event
                    self.raiseEventNoErrors(WebCommand(cmd))
                except StopIteration:
                    time.sleep(3)
                finally:
                    latest = core.db.get_connection().messages.find({"_id": {"$gt": last}}).limit(1)
        except KeyboardInterrupt:
            print "ctrl-c was pressed"
