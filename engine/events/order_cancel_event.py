class OrderCancelEvent:
    """
    Represents a successfully order cancelled response

    Attributes:
        order_id (int): Unique identifier for the order.
    """

    def __init__(self, order_id: int, side: str, quantity: int, price: float):

        """
        Initialize a new OrderCancelEvent

        Args:
            order_id (int): Unique identifier for the order.
        """

        self.order_id = order_id
        self.side = side
        self.quantity = quantity
        self.price = price