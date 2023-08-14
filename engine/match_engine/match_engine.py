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
            self.order_book.delete_order(request)

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

                # Emit trade message
                self.emit_message("Trade", bid_order,
                                  ask_order, trade_quantity)

                if bid_order.quantity > 0:
                    # Add partially filled order back to the book
                    self.order_book.add_order(bid_order)
                else:
                    self.emit_message("OrderFullyFilled", bid_order)

                if ask_order.quantity > 0:
                    # Add partially filled order back to the book
                    self.order_book.add_order(ask_order)
                else:
                    self.emit_message("OrderFullyFilled", ask_order)

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
                    self.emit_message("OrderFullyFilled", resting_order)
                    market_order.quantity -= resting_order.quantity
                else:
                    # Partially fill resting order
                    resting_order.quantity -= market_order.quantity
                    self.order_book.add_order(resting_order)
                    self.emit_message("OrderPartiallyFilled", resting_order)
                    market_order.quantity = 0

            if market_order.quantity > 0:
                self.order_book.add_order(market_order)

        elif market_order.side == "sell":

            # Continue to match with ask orders until we have exhausted quantity
            while self.order_book.bids and market_order.quantity > 0 and self.order_book.bids[0].price >= market_order.price:
                resting_order = self.order_book.remove_best_bid()

                if resting_order.quantity <= market_order.quantity:
                    # Fully fill resting order
                    self.emit_message("OrderFullyFilled", resting_order)
                    market_order.quantity -= resting_order.quantity
                else:
                    # Partially fill resting order
                    resting_order.quantity -= market_order.quantity
                    self.order_book.add_order(resting_order)
                    self.emit_message("OrderPartiallyFilled", resting_order)
                    market_order.quantity = 0

            if market_order.quantity > 0:
                self.order_book.add_order(market_order)

    def process_order_book_snapshot(self) -> None:
        """
        Process a request to get a snapshot of the order book

        Returns:
            None
        """
        response = ""
        for ask in self.order_book.get_asks():
            response += f"#S0{ask.order_id}\t{ask.price}\t{ask.quantity}\n"
        for bid in self.order_book.get_bids():
            response += f"#B0{bid.order_id}\t{bid.price}\t{bid.quantity}\n"
        
        self.message_bus.publish("event", response)

    def emit_message(self, message_type: str, buy_order: Order, sell_order=None, trade_quantity=None) -> None:

        response = ""
        if message_type == "Trade":
            if trade_quantity > 0:
                response = f"Trade: Buy Order {buy_order.order_id} ({buy_order.side}) and Sell Order {sell_order.order_id} ({sell_order.side}) - Quantity: {trade_quantity}, Price: {sell_order.price}"
        
        elif message_type == "OrderFullyFilled":
            response = f"Order {buy_order.order_id} ({buy_order.side}) fully filled at price {buy_order.price}"
        
        elif message_type == "OrderPartiallyFilled":
            response = f"Order {buy_order.order_id} ({buy_order.side}) partially filled at price {buy_order.price}. Remaining quantity: {buy_order.quantity}"

        self.message_bus.publish("event", response)
