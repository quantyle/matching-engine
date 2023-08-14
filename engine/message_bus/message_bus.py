import multiprocessing


class MessageBus:
    def __init__(self):
        self.requests =  multiprocessing.Queue()
        self.events =  multiprocessing.Queue()

    def subscribe(self, message_type):
        if message_type == "request":
            return self.requests
        elif message_type == "event":
            return self.events

    def publish(self, message_type, message):
        if message_type == "request":
            self.requests.put(message)
        elif message_type == "event":
            self.events.put(message)