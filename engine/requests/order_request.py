

class OrderRequest():
    """
    Represents a request to add or cancel an order.

    Attributes:
        order_id (int): Unique identifier for the order.
        side (str): Order side, indicating whether this is a request for a "buy" or "sell" order.
        quantity (int): Order quantity.
        price (float): Order price level.
    """

    def __init__(self, order_id: int, side: str, quantity: int, price: float = None):
        """
        Initialize a new OrderRequest instance.

        Args:
            order_id (int): Unique identifier for the order.
            side (str): Order side, indicating whether this is a request "buy" or "sell" order.
            quantity (int): Order quantity.
            price (float): Order price level.

        Raises:
            TypeError: if any argument has an incorrect type.
        """
        if not isinstance(order_id, int):
            raise TypeError("order_id must be an integer")
        
        if not isinstance(side, str):
            raise TypeError("side must be a string")
        
        if not isinstance(quantity, int):
            raise TypeError("quantity must be an integer")
        
        if price and not isinstance(price, float):
            raise TypeError("price must be a float")
        
        self.order_id = order_id
        self.side = side
        self.quantity = quantity
        self.price = price

