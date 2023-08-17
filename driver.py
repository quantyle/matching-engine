import time
import random
from typing import Union, Any, List
# requests
from engine.requests.add_order_request import AddOrderRequest
from engine.requests.cancel_order_request import CancelOrderRequest
from engine.requests.order_book_snapshot_request import OrderBookSnapshotRequest
# events
from engine.events.trade_event import TradeEvent
from engine.events.order_fully_filled import OrderFullyFilled
from engine.events.order_partially_filled import OrderPartiallyFilled
from engine.events.order_book_snapshot import OrderBookSnapshot
from engine.events.order_cancel_event import OrderCancelEvent

from engine.message_bus.message_bus_client import MessageBusClient

class Driver(MessageBusClient):

    def __init__(self, delay: int=1):
        super().__init__()
        self.delay = delay


    def generate_initial_requests(self) -> List[Any]:
        """
        Generate the initial list of requests that corresponds to the spec sheet

        Returns:
            List[Any]: list of order requests of one or more types
        """
        return [
            # Asks
            AddOrderRequest(order_id=1, side="sell", quantity=1, price=1075.0),
            AddOrderRequest(order_id=2, side="sell", quantity=10, price=1050.0),
            AddOrderRequest(order_id=3, side="sell", quantity=2, price=1025.0),
            AddOrderRequest(order_id=4, side="sell", quantity=5, price=1025.0),

            # Bids
            AddOrderRequest(order_id=5, side="buy", quantity=9, price=1000.0),
            AddOrderRequest(order_id=6, side="buy", quantity=1, price=1000.0),
            AddOrderRequest(order_id=7, side="buy", quantity=30, price=975.0),
            AddOrderRequest(order_id=8, side="buy", quantity=10, price=950.0),
        ]

    def generate_random_orders(self, num_orders: int, max_quantity: int, max_price: float):
        """
        Generate and publish random AddOrderRequest messages to the message bus.

        Args:
            num_orders (int): The number of random orders to generate and publish.
            max_quantity (int): The maximum quantity for the random orders.
            max_price (float): The maximum price for the random orders.

        Returns:
            None
        """
        for _ in range(num_orders):
            side = random.choice(["buy", "sell"])
            quantity = random.randint(1, max_quantity)
            price = random.uniform(1.0, max_price) if side == "buy" else random.uniform(max_price, max_price * 2)
            order = AddOrderRequest(order_id=random.randint(1, 1000), side=side, quantity=quantity, price=price)
            self.publish(order)


    def test_aggressive_buy(self, partial: bool) -> None:
        """
        Simulate an aggressive buy order that matches the example show in the product specification.

        Returns:
            None
        """
        requests = self.generate_initial_requests()
        quantity = 3 if partial else  2
        requests.append(
            # Aggressive order
            AddOrderRequest(order_id=9, side="buy", quantity=quantity, price=1050.0)
        )

        print("testing an aggressive buy order")

        # Get responses
        while True: 
            
            try: 
                order = requests.pop(0)
                self.publish(order)

            except IndexError: 
                pass

            self.publish(OrderBookSnapshotRequest())
            response = self.read()
            self.print_event(response)
            time.sleep(self.delay)

    def test_aggressive_sell(self, partial: bool) -> None:
        """
        Simulate an aggressive buy order that matches the example show in the product specification.

        Returns:
            None
        """
        requests = self.generate_initial_requests()
        quantity = 20 if partial else 30
        requests.append(
            # Aggressive order
            AddOrderRequest(order_id=9, side="sell", quantity=quantity, price=950.0)
        )

        print("testing an aggressive buy order")

        
        # Get responses
        while True: 
            
            try: 
                order = requests.pop(0)
                self.publish(order)

            except IndexError: 
                pass

            self.publish(OrderBookSnapshotRequest())
            response = self.read()
            self.print_event(response)
            time.sleep(self.delay)

    def test_cancel_order(self, side: str) -> None:
        """
        Simulate a cance order of a resting order.

        Returns:
            None
        """

        requests = self.generate_initial_requests()

        if side == "buy":
            requests.append(
                CancelOrderRequest(order_id=8, side="buy", quantity=10, price=950.0)
            )
        elif side == "sell":
            requests.append(
                CancelOrderRequest(order_id=3, side="sell", quantity=2, price=1025.0)
            )
  

        # Get responses
        while True: 
            
            try: 
                order = requests.pop(0)
                self.publish(order)

            except IndexError: 
                pass

            self.publish(OrderBookSnapshotRequest())
            response = self.read()
            self.print_event(response)
            time.sleep(self.delay)

    def print_event(self, message: Any) -> None:
        """
        Prints the message coming from the event bus in a readable format.

        Args:
            message (Union[TradeEvent, OrderPartiallyFilled, OrderFullyFilled, OrderBookSnapshot]):
                The message type to print from the message_bus event channel.

        Returns:
            None
        """
        print(message)

        # if isinstance(message, TradeEvent):
        #     print(f"[TRADE] price: {message.price}, quantity: {message.quantity})")
        # if isinstance(message, OrderCancelEvent):
        #     print(f"[CANCEL] order_id: {message.order_id}, side: {message.side}, quantity: {message.quantity}, price: {message.price})")
        # elif isinstance(message, OrderPartiallyFilled):
        #     print(f"[PARTIAL_FILL] order_id({message.order_id}, remaining_quantity: {message.remaining_quantity}")
        # elif isinstance(message, OrderFullyFilled):
        #     print(f"[FULL_FILL]: order_id {message.order_id}")
        # elif isinstance(message, OrderBookSnapshot):
        #     print(f"[BOOK_SNAPSHOT]: \n{message.snapshot}")
        # else: 
        #     raise TypeError("incorrect message type")

