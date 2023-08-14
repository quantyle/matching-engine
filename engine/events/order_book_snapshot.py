class OrderBookSnapshot:
    """
    Represents a snapshot of the current order book

    Attributes:
        snapshot (str): A string representing the current order book.
    """

    def __init__(self, snapshot: str):

        """
        Initialize a new instnce of OrderBookSnapshot.

        Args:
            snapshot (str): A string representing the current order book.
        
        """

        self.snapshot = snapshot