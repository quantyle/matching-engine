

class OrderPartiallyFilled:
    """
    Represents a partially filled order message

    Attributes:
        order_id (int): Unique identifier for the order.
        remaining_quantity (int): Remaining trade quantity after partial fill.
    """

    def __init__(self, order_id: int, remaining_quantity: int):
        """
        Initialize a new OrderFullyFilled instance.

        Args:
            order_id (int): Unique identifier for the order.
            remaining_quantity (int): The remaining quantity after the partial fill.
        
        Raises:
            TypeError: if any argument has an incorrect type.
        """

        if not isinstance(order_id, int):
            raise TypeError("price must be a float")
        
        if not isinstance(remaining_quantity, int):
            raise TypeError("remaining quantity must be an integer")
        
        self.order_id = order_id
        self.remaining_quantity = remaining_quantity
