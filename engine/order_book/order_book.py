import heapq
from typing import List, Optional
from ..orders.order import Order
from ..requests.cancel_order_request import CancelOrderRequest

class OrderBook:
    """
    Represents an Order Book (the main data structure to track bids and asks).

    Attributes:
        bids (list): Priority queue for bids (max heap)
        asks (list): Priority queue for asks (min heap)
        _bids_positions (dict): A dictionary that maps order_id's to position in the bids heap
        _asks_positions (dict): A dictionary that maps order_id's to position in the asks heap
    """

    def __init__(self):
        """
        Initialize a new OrderBook instance
        """
        self.bids = []
        self.asks = [] 
        self._bids_positions = {} 
        self._asks_positions = {} 

    def add_order(self, order: Order) -> None:
        """
        Adds a single order to the order book

        Args:
            order (Order): Order object to add to book (either side)
        """
        if order.side == "buy":
            heapq.heappush(self.bids, order)
            self._bids_positions[order.order_id] = len(self.bids) - 1

        elif order.side == "sell":
            heapq.heappush(self.asks, order)
            self._asks_positions[order.order_id] = len(self.asks) - 1

    def remove_best_bid(self) -> Order:
        """
        Removes the best bid order from the book.

        Returns: 
            Order: returns the best bid order.
        """
        if self.bids:
            best_bid_order = heapq.heappop(self.bids)
            del self._bids_positions[best_bid_order.order_id]
            return best_bid_order
    
    def remove_best_ask(self) -> Order:
        """
        Removes the best ask order from the book.

        Returns:
            Order: returns the best ask order.
        """
        if self.asks:
            best_ask_order = heapq.heappop(self.asks)
            del self._asks_positions[best_ask_order.order_id]
            return best_ask_order

    def delete_order(self, order_id: int) -> None:
        """
        Deletes a specific order from the book at any position (price level).

        Args:
            order_id (int): The order_id of the order to cancel.
        """

        # @NOTE We leverage a hashmap here to keep track of order_id's and their positions for O(log(n)) deletion, instead of O(n)
        # @NOTE This is important since many requests in traditional markets are requests for deletions 

        if order_id in self._bids_positions:
            position = self._bids_positions.pop(order_id)
            if position < len(self.bids):
                last_order = self.bids.pop()
                if position != len(self.bids):
                    self.bids[position] = last_order
                    self._bids_positions[last_order.order_id] = position

        elif order_id in self._asks_positions:
            position = self._asks_positions.pop(order_id)
            if position < len(self.asks):
                last_order = self.asks.pop()
                if position != len(self.asks):
                    self.asks[position] = last_order
                    self._asks_positions[last_order.order_id] = position
        else:
            raise KeyError("order_id not found in order book")
            

    def get_best_bid(self) -> Optional[Order]:
        """
        Gets the current best bid from the order book.

        Returns:
            Optional[Order]: The order object at the current best bid in the book
        """
        if self.bids:
            return self.bids[0]
        return None

    def get_best_ask(self) -> Optional[Order]:
        """
        Gets the current best asl from the order book.

        Returns:
            Optional[Order]: The order object at the current best ask in the book
        """
        if self.asks:
            return self.asks[0]
        return None

    def get_bids(self, n: int = None) -> List[Order]:
        """
        Read-only representation of the ordeer book on the bids side at depth of n

        Args: 
            n (int): the depth of the order book bids to retreive.
        
        Returns: 
            List[Order]: A list of all bid orders, unless depth n is provided. 

        """
        if n == None: 
            return sorted([bid for bid in self.bids], key=lambda order: order.price, reverse=True)
        return sorted([bid for bid in self.bids[:n]], key=lambda order: order.price, reverse=True)


    def get_asks(self, n: int = None) -> List[Order]:
        """
        Read-only representation of the ordeer book on the asks side at depth of n
        
        Args: 
            n (int): the depth of the order book asks to retrieve.
        
        Returns: 
            List[Order]: A list of all ask orders, unless depth n is provided. 
        """
        if n == None: 
            return sorted([ask for ask in self.asks], key=lambda order: order.price, reverse=True)
        return sorted([ask for ask in self.asks[:n]], key=lambda order: order.price, reverse=True)

    def validate_book(self) -> bool:
        """
        Checks if the heaps for ask and bids are their respective positions hashmaps

        Returns:
            bool: the result of: len(self.asks) == len(self._asks_positions.keys()) and len(self.bids) == len(self._bids_positions.keys())
        """
        return len(self.asks) == len(self._asks_positions.keys()) and len(self.bids) == len(self._bids_positions.keys())
    