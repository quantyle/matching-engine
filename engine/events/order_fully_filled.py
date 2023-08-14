class OrderFullyFilled:
    """
    Represents a fully filled order message

    Attributes:
        order_id (int): Unique identifier for the order.
    """

    def __init__(self, order_id: int):

        """
        Initialize a new OrderFullyFilled instance.

        Args:
            order_id (int): Unique identifier for the order.
        
        Raises:
            TypeError: if any argument has an incorrect type.
        """
        if not isinstance(order_id, int):
            raise TypeError("price must be a float")

        self.order_id = order_id