

class TradeEvent:
    """
    Represents a trade event that has occured.

    Attributes:
        price (float): Trade price level.
        quantity (int): Trade quantity.
    """

    def __init__(self, price: float, quantity: int):
        """
        Initialize a new TradeEvent instance.

        Args:
            price (float): Order price level
            quantity (int): Order quantity.

        Raises:
            TypeError: if any argument has an incorrect type.
        """
        if not isinstance(price, float):
            raise TypeError("price must be a float")
        
        if not isinstance(quantity, int):
            raise TypeError("quantity must be an integer")

        self.price = price
        self.quantity = quantity

