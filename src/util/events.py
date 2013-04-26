class Event(object):
    pass

class Eventful(object):
    def __init__(self):
        self.events = {}
    
    def add_event(self, key):
        """
        Register an event type.
        @param key Event name to be registered
        """
        if not key in self.events:
            self.events[key] = []
 
    def add_listener(self, key, func):
        """
        Register a function to be called on event.
        @param key Event name
        @param func Function to be called on event
        """
        if key in self.events:
            self.events[key].append(func)
            
    def handle_event(self, key, event):
        """
        Call all functions listening to event.
        @param key Event name
        @param event Event object to be sent to functions
        """
        try:
            for f in self.events[key]:
                try:
                    f(event)
                except TypeError as exc:
                    print("Error::" + str(exc))
        except KeyError as exc:
            print("Error::" + str(exc))
