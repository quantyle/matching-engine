"""
main.py: A driver program used to test the matching engine
"""

import time
from typing import Union
from engine.requests.add_order_request import AddOrderRequest
from engine.requests.cancel_order_request import CancelOrderRequest
from engine.requests.order_book_snapshot_request import OrderBookSnapshotRequest
from engine.match_engine.match_engine import MatchEngine
from engine.message_bus.message_bus import MessageBus
# events
from engine.events.trade_event import TradeEvent
from engine.events.order_fully_filled import OrderFullyFilled
from engine.events.order_partially_filled import OrderPartiallyFilled
from engine.events.order_book_snapshot import OrderBookSnapshot

# class InputOrderRequestGenerator:
#     def generate_random_order(self, order_id):
#         side = random.choice(["buy", "sell"])
#         quantity = random.randint(10, 200)
#         price = round(random.uniform(40.0, 60.0), 2)
#         return Order(order_id, side, quantity, price)

#     def generate_random_message(self, order_id):
#         message_type = random.choice(
#             ["TradeEvent", "OrderFullyFilled", "OrderPartiallyFilled"])

#         if message_type == "TradeEvent":
#             price = round(random.uniform(45.0, 55.0), 2)
#             quantity = random.randint(10, 50)
#             return TradeEvent(order_id, price, quantity)

#         if message_type == "OrderFullyFilled":
#             return OrderFullyFilled(order_id)

#         if message_type == "OrderPartiallyFilled":
#             remaining_quantity = random.randint(1, 30)
#             return OrderPartiallyFilled(order_id, remaining_quantity)


class Driver:

    def __init__(self):
        self.delay = 1
        self.message_bus = MessageBus()
        self.match_engine = MatchEngine(self.message_bus)
        self.match_engine.start()

    def test_aggressive_buy(self) -> None:
        """
        Simulate an aggressive buy order that matches the example show in the product specification.

        Returns:
            None
        """
        resting_order_queue = [
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

            # Aggressive order
            AddOrderRequest(order_id=9, side="buy", quantity=3, price=1050.0)
        ]


        # subscribe to the events channel
        responses = self.message_bus.subscribe("event")       

        # get responses
        while True: 
            
            try: 
                order = resting_order_queue.pop(0)
                self.message_bus.publish("request", order)

            except IndexError: 
                pass

            self.message_bus.publish("request", OrderBookSnapshotRequest())
            response = responses.get()
            self.print_event(response)
            time.sleep(self.delay)

    def print_event(self, message: Union[TradeEvent, OrderPartiallyFilled, OrderFullyFilled, OrderBookSnapshot]) -> None:
        if isinstance(message, TradeEvent):
            print(f"[TRADE] price: {message.price}, quantity: {message.quantity})")
        elif isinstance(message, OrderPartiallyFilled):
            print(f"[PARTIAL_FILL] order_id({message.order_id}, remaining_quantity: {message.remaining_quantity})")
        elif isinstance(message, OrderFullyFilled):
            print(f"[FULL_FILL]: order_id {message.order_id}")
        elif isinstance(message, OrderBookSnapshot):
            print(f"[BOOK]: \n{message.snapshot}")



# Driver application
if __name__ == "__main__":

    driver = Driver()
    driver.test_aggressive_buy()
    # driver.test_aggressive_sell()






