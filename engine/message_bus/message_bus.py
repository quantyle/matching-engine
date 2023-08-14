import multiprocessing


class MessageBus:
    """
    Represents the message bus for inteprocess communication.

    Attributes:
        requests (multiprocessing.Queue): The requests channel.
        events (multiprocessing.Queue): The events channel.
    """

    def __init__(self):
        self.requests =  multiprocessing.Queue()
        self.events =  multiprocessing.Queue()

    def subscribe(self, channel: str) ->  multiprocessing.Queue:
        """
        Subscribe to a specific channel.

        Args:
            channel (str): The specific channel to subscribe to.

        Returns:
            multiprocessing.Queue: A reference to the multiprocessing.Queue for the specified channel
        """
        if channel == "request":
            return self.requests
        elif channel == "event":
            return self.events

    def publish(self, channel: str, message) -> None:
        """
        Subscribe to a specific channel.

        Args:
            channel (str): The specific channel to publish to.

        Returns:
            None
        """
        if channel == "request":
            self.requests.put(message)
        elif channel == "event":
            self.events.put(message)