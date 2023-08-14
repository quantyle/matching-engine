from .order_request import OrderRequest

class CancelOrderRequest(OrderRequest):
    """
    Represents a request to cancel an existing order.

    Attributes:
        order_id (int): Unique identifier for the order.
        side (str): Order side, indicating whether this is a request for a "buy" or "sell" order.
        quantity (int): Order quantity.
        price (float): Order price level.
    """

    def __init__(self, order_id: int, side: str, quantity: int, price: float):
        """
        Initialize a new AddOrderRequest instance.

        Args:
            order_id (int): Unique identifier for the order.
            side (str): Order side, indicating whether this is a request "buy" or "sell" order.
            quantity (int): Order quantity.
            price (float): Order price level.

        Raises:
            TypeError: if any argument has an incorrect type.
        """
        super().__init__(order_id, side, quantity, price)