class Order:

    """
    Represents an Order (either limit or market order).

    Attributes:
        order_id (int): Unique identifier for the order.
        side (str): Order side, indicating whether it's a "buy" or "sell" order.
        quantity (int): Order quantity.
        price (float): Order price level.
    """

    def __init__(self, order_id: int, side: str, quantity: int, price: float = None):
        """
        Initialize a new Order instance.

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


    def __lt__(self, other) -> bool:
        """
        Compare two orders based on their prices and sides for priority in a priority queue.

        Args:
            other (Order): The other order to compare with.

        Returns:
            bool: True if this order has higher priority, False otherwise.
        """
        if self.side == "buy":
            return self.price > other.price  # For bids, higher price has higher priority
        elif self.side == "sell":
            return self.price < other.price  # For asks, lower price has higher priority

    def __eq__(self, other) -> bool:
        """
        Compare two orders based on their prices for equality.

        Args:
            other (Order): The other order to compare with.

        Returns:
            bool: True if the prices of the orders are equal, False otherwise.
        """
        return self.price == other.price
