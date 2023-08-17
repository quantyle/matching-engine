"""
main.py: A driver program used to test the matching engine
"""

import time
from driver import Driver
from engine.match_engine.match_engine import MatchEngine
from engine.message_bus.message_bus import  MessageBus

# Driver application
if __name__ == "__main__":

    # start the matching engine
    match_engine = MatchEngine()
    match_engine.start()

    # # start the message bus
    # message_bus = MessageBus('localhost', 8888)
    # message_bus.start()

    # time.sleep(4)

    # # start the driver code
    # driver = Driver()
    # driver.test_aggressive_buy(partial=True)



# """
# main.py: A driver program used to test the matching engine
# """

# import sys
# import argparse
# from driver import Driver

# def main() -> None:
#     """
#     Entry point for the program.

#     Returns:
#         None
#     """

#     parser = argparse.ArgumentParser(description="Driver program for Matching Engine. \nRun 'python3 main.py --test buy_partial' for base example")
    
#     tests = "buy_partial | buy_full | sell_partial | sell_full | cancel_buy | cancel_sell" 

#     # Add your arguments here
#     parser.add_argument("--test", type=str, help=f"The type of test to run [ {tests} ]")
#     parser.add_argument("--delay", type=str, help="The delay in seconds between event and requests parses (this does not block the actual MatchEngine class)")

#     args = parser.parse_args()

#     if args.test is not None:
        
#         delay = args.delay if args.delay is not None else 1
#         # insantiate the driver
#         driver = Driver(delay)

#         # grab the argument for test type
#         test_type = args.test

#         if test_type == "buy_partial":
#             driver.test_aggressive_buy(partial=True)
#         elif test_type == "buy_full":
#             driver.test_aggressive_buy()
#         elif test_type == "sell_partial":
#             driver.test_aggressive_sell(partial=True)
#         elif test_type == "sell_full":
#             driver.test_aggressive_sell()
#         elif test_type == "cancel_buy":
#             driver.test_cancel_order(side="buy")
#         elif test_type == "cancel_sell":
#             driver.test_cancel_order(side="sell")
#     else:
#         parser.print_help(sys.stderr)



# # Driver application
# if __name__ == "__main__":
#     main()

