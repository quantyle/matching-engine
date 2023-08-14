import multiprocessing
from typing import Union
# order and order book
from ..orders.order import Order
from ..order_book.order_book import OrderBook
# requests
from ..requests.add_order_request import AddOrderRequest
from ..requests.cancel_order_request import CancelOrderRequest
from ..requests.order_book_snapshot_request import OrderBookSnapshotRequest
from ..message_bus.message_bus import MessageBus
# events
from ..events.trade_event import TradeEvent
from ..events.order_fully_filled import OrderFullyFilled
from ..events.order_partially_filled import OrderPartiallyFilled
from ..events.order_book_snapshot import OrderBookSnapshot
from ..events.order_cancel_event import OrderCancelEvent

class MatchEngine(multiprocessing.Process):
    """
    Represents the core matching engine, which takes in requests to be processed and emits messages via the MessageBus.

    Attributes:
        order_book (OrderBook): An instance or OrderBook to keep track of all orders.
    """

    def __init__(self, message_bus: MessageBus):
        super().__init__()
        self.order_book = OrderBook()
        self.message_bus = message_bus

    def run(self):
        """
        Run the Match Engine process. Overrides the multiprocessing.Process.run() function
        """

        # Subscribe to the requests channel
        requests = self.message_bus.subscribe(message_type="request")

        while True:
            # Block here until we get a request
            request = requests.get()

            # Process the incoming request
            self.process(request)

            # if self.order_book.validate_book():
            #     print("book valid")
            # else:
            #     print("book invalid")


    def process(self, request: Union[AddOrderRequest, CancelOrderRequest, OrderBookSnapshotRequest]) -> None:
        """
        Process any incoming request.

        Args:
            request (Union[AddOrderRequest, CancelOrderRequest, OrderBookSnapshotRequest]):
                The incoming request to process. It can be a request to add an order,
                cancel an order, or get an order book snapshot.

        Returns:
            None
        """

        # Check if the request is to add a new order
        if isinstance(request, AddOrderRequest):
            self.process_order(request)

        # Check if the request is one to cancel the order
        elif isinstance(request, CancelOrderRequest):
            self.order_book.delete_order(request.order_id)
            self.emit_cancel_order(request)

        # Check if the request is one to get a snapshot of the orderbook
        elif isinstance(request, OrderBookSnapshotRequest):
            self.process_order_book_snapshot()

    def process_order(self, request: AddOrderRequest) -> None:
        """
        Process an incoming request of type AddOrderRequest.

        Args:
            request (AddOrderRequest): the request to be processed

        Returns:
            None
        """
        if request.price:
            limit_order = Order(**vars(request))
            self.process_limit_order(limit_order)

        elif request.price == None:
            market_order = Order(**vars(request))
            self.process_market_order(market_order)
        
    def process_limit_order(self, limit_order: Order) -> None:
        """
        Process a limit order by adding it to the order book and performing matching.

        Args:
            limit_order (Order): The limit order to be processed.

        Returns:
            None
        """

        self.order_book.add_order(limit_order)

        # Perform matching algo
        while self.order_book.bids and self.order_book.asks:

            # Get the current best bid and best ask
            best_bid = self.order_book.get_best_bid()
            best_ask = self.order_book.get_best_ask()

            # If the following evaluates to True, then a trade has occured
            if best_bid.price >= best_ask.price:

                # Pop the orders from the heaps
                bid_order = self.order_book.remove_best_bid()
                ask_order = self.order_book.remove_best_ask()

                # Get the min quantity
                trade_quantity = min(bid_order.quantity, ask_order.quantity)

                # Update order quantities
                bid_order.quantity -= trade_quantity
                ask_order.quantity -= trade_quantity

                # Emit a Trade event
                self.emit_trade(bid_order.price, trade_quantity)
                self.emit_trade(ask_order.price, trade_quantity)


                if bid_order.quantity > 0:
                    # Add partially filled order back to the book
                    self.order_book.add_order(bid_order)
                    self.emit_partial_fill(bid_order.order_id, bid_order.quantity)
                else:
                    # Emit fully filled message
                    self.emit_fully_filled(bid_order.order_id)

                if ask_order.quantity > 0:
                    # Add partially filled order back to the book
                    self.order_book.add_order(ask_order)
                    self.emit_partial_fill(ask_order.order_id, ask_order.quantity)
                else:
                    # Emit fully filled message
                    self.emit_fully_filled(ask_order.order_id)

            else:
                break

    def process_market_order(self, market_order: Order) -> None:
        """
        Process an incoming match order.

        Args:
            market_order (Order): The market order to be matched.

        Returns:
            None
        """
        if market_order.side == "buy":

            # Continue to match against bid orders until we have exhausted quantity
            while self.order_book.asks and market_order.quantity > 0 and self.order_book.asks[0].price <= market_order.price:
                resting_order = self.order_book.remove_best_ask()

                if resting_order.quantity <= market_order.quantity:
                    # Fully fill resting order
                    self.emit_trade(resting_order.price, market_order.quantity)
                    self.emit_fully_filled(resting_order.order_id)
                    market_order.quantity -= resting_order.quantity
                else:
                    # Partially fill resting order
                    resting_order.quantity -= market_order.quantity
                    self.order_book.add_order(resting_order)
                    self.emit_trade()
                    self.emit_partial_fill(resting_order.order_id, resting_order.quantity)
                    market_order.quantity = 0

            if market_order.quantity > 0:
                self.order_book.add_order(market_order)

        elif market_order.side == "sell":

            # Continue to match with ask orders until we have exhausted quantity
            while self.order_book.bids and market_order.quantity > 0 and self.order_book.bids[0].price >= market_order.price:
                resting_order = self.order_book.remove_best_bid()

                if resting_order.quantity <= market_order.quantity:
                    # Fully fill resting order
                    self.emit_trade(resting_order.price, market_order.quantity)
                    self.emit_fully_filled(resting_order.order_id)
                    market_order.quantity -= resting_order.quantity
                else:
                    # Partially fill resting order
                    resting_order.quantity -= market_order.quantity
                    self.order_book.add_order(resting_order)
                    self.emit_trade()
                    self.emit_partial_fill(resting_order.order_id, resting_order.quantity)
                    market_order.quantity = 0

            if market_order.quantity > 0:
                self.order_book.add_order(market_order)



    def emit_trade(self, price: float, quantity: int) -> None:
        """
        Publishes a trade message to the message bus.

        Args:
            price (float): Indicates the price at which the trade happened.
            quantity (int): the amount that traded.

        Returns:
            None
        """

        response = TradeEvent(price, quantity)
        self.message_bus.publish("event", response)
        

    def emit_fully_filled(self, order_id: int) -> None:
        """
        Publishes a fully filled message to the message bus

        Args:
            order_id (int): Unique identifier of the order that was fully filled.

        Returns:
            None
        """

        response = OrderFullyFilled(order_id)
        self.message_bus.publish("event", response)

    def emit_partial_fill(self, order_id: int, remaining_quantity: int) -> None:
        """
        Publishes a partially filled message to the message bus

        Args:
            order_id (int): Unique identifier of the order that was fully filled.
            remaining_quantity (int): The amount remaining. 
        Returns:
            None
        """
        response = OrderPartiallyFilled(order_id, remaining_quantity)
        self.message_bus.publish("event", response)
    
    def emit_cancel_order(self, message: OrderCancelEvent) -> None:
        response = OrderCancelEvent(**vars(message))
        self.message_bus.publish("event", response)

    def process_order_book_snapshot(self) -> None:
        """
        Process a request to get a snapshot of the order book

        Returns:
            None
        """

        response = "\n"
        for ask in self.order_book.get_asks():
            response += f"#S0{ask.order_id}\t{ask.price}\t{ask.quantity}\n"
        response += "\n"
        for bid in self.order_book.get_bids():
            response += f"#B0{bid.order_id}\t{bid.price}\t{bid.quantity}\n"

        self.message_bus.publish("event", OrderBookSnapshot(response))

    def next_order_id(self) -> int:
        return len(self.order_book.asks) + len(self.order_book.bids)


    def reset_book(self) -> None:
        """
        Resets the order book, for testing purposes mostly 

        Returns:
            None
        """
        self.order_book = OrderBook()